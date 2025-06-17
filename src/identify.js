import {xu} from "xu";
import {XLog} from "xlog";
import {fileUtil, encodeUtil} from "xutil";
import {formats} from "./format/formats.js";
import {FileSet} from "./FileSet.js";
import {DexFile} from "./DexFile.js";
import {Identification} from "./Identification.js";
import {getDetections} from "./Detection.js";
import {DEXRPC_HOST, DEXRPC_PORT} from "./dexUtil.js";
import {UInt8ArrayReader} from "UInt8ArrayReader";

// matches the given value against the matcher. If 'matcher' is a string, then value just needs to start with matcher, unless fullStringMatch is set then the entire string must be a case insensitive match. If 'matcher' is a regexp, it must regex match value.
function flexMatch(value, matcher, fullStringMatch)
{
	return ((typeof matcher==="string" && (fullStringMatch ? (value.toLowerCase()===matcher.toLowerCase()) : value.toLowerCase().startsWith(matcher.toLowerCase()))) || (matcher instanceof RegExp && value.match(matcher)));
}
export {flexMatch};

// A list of family types. Order is the secondary order they will be matched in the case of multiple 'types' of matches (magic, etc, filename) across multiple categories
const FAMILY_MATCH_ORDER = ["archive", "document", "audio", "music", "video", "image", "poly", "font", "text", "executable", "other"];

// list of 'meta' keys that may appear as fileMeta[k] or in the result of a program r.meta[k] that should always be inherited and exposed in the file meta itself
export const ID_META_INHERIT = ["macFileType", "macFileCreator", "proDOSType", "proDOSTypeCode", "proDOSTypePretty", "proDOSTypeAux"];

async function getMacBinaryMeta(inputFile, debug)
{
	// MacBinary 1 Specs: https://web.archive.org/web/19991103230427/http://www.lazerware.com:80/formats/macbinary/macbinary.html
	// MacBinary 2 Specs: https://files.stairways.com/other/macbinaryii-standard-info.txt

	// MacBinary header is 128 bytes
	if(inputFile.size<128)
		return debug ? `File size ${inputFile.size} is less than 128 bytes` : false;

	const header = await fileUtil.readFileBytes(inputFile.absolute, 128);
	if([0, 74, 82].some(v => header[v]!==0))
		return debug ? `Header bytes 0, 74, and 82 must be 0` : false;

	if(header[1]>63)	// Also used to fail if header[1]<1 but then I discovered a file that has a header[1] of 0 (test/sample/audio/fssdSound/LABSLAB.SOU)
		return debug ? `Header byte 1 must be between 1 and 63` : false;

	if(header[2]===0)	// don't allow the first byte of the filename to be zero
		return debug ? `First byte of filename cannot be 0` : false;

	const dataForkLength = header.getUInt32BE(83);
	const resourceForkLength = header.getUInt32BE(87);
	if(dataForkLength===0 && resourceForkLength===0)	// according to the docs, there is also an upper limit to these sizes, but I don't currently check that
		return debug ? `Data fork length (${dataForkLength}) and resource fork length (${resourceForkLength}) cannot both be 0` : false;

	if((dataForkLength+128)>inputFile.size)	// I used to add resourceForkForkLength+128 but I encountered a file where that's not true (test/sample/audio/fssdSound/IFALLEN.SOU)
		return debug ? `Data fork length (${dataForkLength}) + 128 header extends beyond file size (${inputFile.size})` : false;

	const suspectForkSizes = (dataForkLength+resourceForkLength+128)>inputFile.size || (dataForkLength+128+resourceForkLength+128+128+4096)<inputFile.size;	// later half extra 128's are to align on 128 byte boundaries, extra 4096 is just to allow some allowances

	// we used to check and forbid any null bytes in type/creator, but I've encountered macbinary files that have no type/creator (archive/macBinary/Icon↵) so we'll allow it
	// instead we detect if it's suspect and then later on if some other checks also look suspect we return false
	const fileTypeData = header.subarray(65, 69);
	const suspectFileType = fileTypeData.indexOfX(0)!==-1;

	const fileCreatorData = header.subarray(69, 73);
	const suspectFileCreator = fileCreatorData.indexOfX(0)!==-1;

	const creationDate = header.getUInt32BE(91);
	const modifiedDate = header.getUInt32BE(95);

	// ensure our modified date is not more than 2 days after our creation date (we've seen a few in the wild that are off by small amount, like 90 seconds (archive/macBinary/ZEN.HLP))
	// I used to do the following check, but I've encountered files (image/macPaint/elvis.mac) where the creation date is after the modified date by a lot, so we'll skip this check
	// so now we just use this as another point of information that a file is suspect
	const suspectDateDifference = (creationDate-modifiedDate)>((xu.DAY*2)/1000);

	const MIN_YEAR = 1972;
	// ensure sane timestamps (year between MIN_YEAR and current year) the format is secs since Mac epoch of 1904, but I've seen unix epoch instead (archive/sit/fixer.sit && archive/diskCopyImage/King.img.bin) so check both
	// we also allow anything in the year 1904/1970 just because we've seen it in the wild (archive/macromediaProjector/MEGACUTE Vol.2) (also 1903 because sometimes the date conversion ends up being that, probably timezone thing on linux? dunno.)
	// we also allow files that have a zero date because we've seen that in the wild too (archive/macBinary/Desktop)
	const currentYear = (new Date()).getFullYear();
	const macTSToDate = v => (new Date((v * 1000) + (new Date("1904-01-01T00:00:00Z")).getTime()));
	const suspectDates = {Creation : false, Modified : false};
	const validateDate = (v, type) =>
	{
		if(v===0)
		{
			suspectDates[type] = true;
			return true;
		}

		const dateMacYear = macTSToDate(v).getFullYear();
		const dateUnixYear = new Date(v*1000).getFullYear();
		if(((dateMacYear<MIN_YEAR && ![1903, 1904].includes(dateMacYear)) || dateMacYear>(currentYear+1)) &&
			((dateUnixYear<MIN_YEAR && ![1969, 1970].includes(dateUnixYear)) || dateUnixYear>(currentYear+1)))
			suspectDates[type] = true;
		
		if((dateMacYear<MIN_YEAR || dateUnixYear<MIN_YEAR))
			suspectDates[type] = true;

		return true;
	};

	const creationDateValid = validateDate(creationDate, "Creation");
	if(creationDateValid!==true)
		return creationDateValid;

	const modifiedDateValid = validateDate(modifiedDate, "Modified");
	if(modifiedDateValid!==true)
		return modifiedDateValid;

	// check to see if we have too many 'suspect' things (2 or more) and return false in that case (image/paintPro/AGIGATE.RSC)
	const suspects = [suspectForkSizes, suspectFileType || suspectFileCreator, suspectDateDifference || suspectDates.Creation || suspectDates.Modified].filter(Boolean);
	if(suspects.length>0)	// eslint-disable-line sonarjs/no-collapsible-if
	{
		// the 16-bit CRC value at offset 124 is a 16-bit CRC-CCITT (XMODEM) of the first 124 bytes of the header
		// this works for most files, but I've encountered too many files where the CRC isn't correct, likely was calculated incorrectly or used an incorrect algo
		// a LOT of files don't have a valid CRC, so we don't check it anymore
		//const crcValue = header.getUInt16BE(124);
		//if(crcValue!==0 && crcValue!==await hashUtil.hashData("CRC-16/XMODEM", header.subarray(0, 124)))
		//	suspects.push(true);

		if(suspects.length>=2)	// eslint-disable-line unicorn/no-lonely-if
			return debug ? `Too many suspect parts: suspectForkSizes:${suspectForkSizes} (${dataForkLength}+${resourceForkLength} : ${inputFile.size}) suspectFileType:${suspectFileType} suspectFileCreator:${suspectFileCreator} suspectDates:${Object.entries(suspectDates).map(([k, v]) => `suspectDates.${k}:${v}`).join(", ")} suspectDateDifference:${suspectDateDifference}` : false;
	}

	return { macFileType : await encodeUtil.decodeMacintosh({data : fileTypeData}), macFileCreator : await encodeUtil.decodeMacintosh({data : fileCreatorData})};	// mac type/creator codes are always roman, so don't specify a region here
}

async function getAppleDoubleMeta(inputFile, debug)
{
	// AppleDouble format: /mnt/compendium/documents/books/AppleSingle_AppleDouble.pdf
	const magics = await fileUtil.readFileBytes(inputFile.absolute, 26);
	if(magics.getUInt32BE(0)!==0x00_05_16_07 || magics.getUInt32BE(4)!==0x00_02_00_00)
		return debug ? `Invalid AppleDouble magic bytes` : false;

	const numEntries = magics.getUInt16BE(24);
	if(numEntries<1 || (numEntries*12)+26>inputFile.size)
		return debug ? `Invalid AppleDouble number of entries ${numEntries}` : false;

	const br = new UInt8ArrayReader(await fileUtil.readFileBytes(inputFile.absolute, 26+(numEntries*12)), {endianness : "be"});
	br.skip(26);
	const entries = [];
	const ENTRY_TYPE_MAP = {
		1 : "dataFork",
		2 : "resourceFork",
		3 : "realName",
		4 : "comment",
		5 : "iconBW",
		6 : "iconColor",
		8 : "fileDates",
		9 : "finderInfo",
		10 : "macFileInfo",
		11 : "prodosFileInfo",
		12 : "msDosFileInfo",
		13 : "afpShortName",
		14 : "afpFileInfo",
		15 : "afpDirectoryId"
	};
	for(let i=0;i<numEntries;i++)
	{
		const entry = {};
		entry.entryid = br.uint32();
		entry.entryType = ENTRY_TYPE_MAP[entry.entryid];
		entry.offset = br.uint32();
		entry.length = br.uint32();
	
		entries.push(entry);
	}

	if(!entries.some(entry => entry.entryType==="resourceFork"))
		return debug ? `No resourceFork entry found in AppleDouble file` : false;

	const finderInfo = entries.find(entry => entry.entryType==="finderInfo");
	if(!finderInfo)
		return debug ? `No finderInfo entry found in AppleDouble file` : false;

	if(finderInfo.offset+finderInfo.length>inputFile.size)
		return debug ? `finderInfo entry extends beyond file size` : false;

	// finder info detailed as 'TYPE FInfo = RECORD' on page 139 of: /mnt/compendium/documents/books/InsideMacintosh/Inside_Macintosh_Volume_II_1985.pdf
	const typeCreatorData = await fileUtil.readFileBytes(inputFile.absolute, 8, finderInfo.offset);
	return {macFileType : await encodeUtil.decodeMacintosh({data : typeCreatorData.subarray(0, 4)}), macFileCreator : await encodeUtil.decodeMacintosh({data : typeCreatorData.subarray(4, 8)})};
}
export {getMacBinaryMeta, getAppleDoubleMeta};

// Get mac file type and creator code, either from inputFile meta (passed in originally by fileMeta argument) or checking if it's a MacBinary file and getting it from that
export async function getIdMeta(inputFile)
{
	const idMeta = {};
	
	// check to see if any of our keys are on our inputFile meta and copy them over as idMeta
	for(const k of ID_META_INHERIT)
	{
		if(inputFile.meta?.[k])
			idMeta[k] = inputFile.meta[k];
	}

	if(!idMeta.macFileType || !idMeta.macFileCreator)
		Object.assign(idMeta, (await getMacBinaryMeta(inputFile)) || {});
	if(!idMeta.macFileType || !idMeta.macFileCreator)
		Object.assign(idMeta, (await getAppleDoubleMeta(inputFile)) || {});

	return idMeta;
}

export async function identify(inputFileRaw, {xlog : _xlog, logLevel="info"}={})
{
	const xlog = _xlog || new XLog(logLevel);

	const inputFile = inputFileRaw instanceof DexFile ? inputFileRaw : await DexFile.create(inputFileRaw);
	if(inputFile.isDirectory)
		return {ids : [Identification.create({from : "dexvert", confidence : 100, magic : "directory", family : "other", formatid : "directory", matchType : "magic", unsupported : true})]};

	// if it's a symlink, we're done!
	if(inputFile.isSymlink)
		return {ids : [Identification.create({from : "dexvert", confidence : 100, magic : "symlink", family : "other", formatid : "symlink", matchType : "magic"})]};

	const f = await FileSet.create(inputFile.root, "input", inputFile);
	const detections = await getDetections(f, {xlog});

	xlog.debug`raw detections:\n${detections.map(v => v?.pretty("\t") || v).join("\n")}`;

	const otherFiles = (await (await fileUtil.tree(f.root, {depth : 1, nodir : true})).parallelMap(async v => await DexFile.create(v))).filter(file => !!file && file.absolute!==f.input.absolute);
	const otherDirs = (await (await fileUtil.tree(f.root, {depth : 1, nofile : true})).parallelMap(async v => await DexFile.create(v))).filter(file => !!file);

	// find the largest byteChecks check and read that many bytes in
	const byteCheckMaxSize = Object.values(formats).flatMap(format => Array.force(format.byteCheck || [])).map(byteCheck => byteCheck.offset+byteCheck.match.length).max();
	let byteCheckBuf = null;
	if(await fileUtil.exists(f.input.absolute))
		byteCheckBuf = await fileUtil.readFileBytes(f.input.absolute, byteCheckMaxSize);

	const idMetaData = await getIdMeta(inputFile);
	xlog.debug`idMetaData for ${inputFile.absolute}:\n${idMetaData}`;

	const matchesByFamily = {magic : [], ext : [], filename : [], fileSize : [], custom : [], idMeta : [], fallback : []};
	for(const familyid of FAMILY_MATCH_ORDER)
	{
		const familyMatches = {magic : [], ext : [], filename : [], fileSize : [], custom : [], idMeta : [], fallback : []};
		for(const [formatid, format] of Object.entries(formats).sortMulti([([, vf]) => FAMILY_MATCH_ORDER.indexOf(vf.familyid), ([, vf]) => vf.formatid], [false, false]))	// the sortMulti ensures we have a predictable order
		{
			if(!FAMILY_MATCH_ORDER.includes(format.familyid))
				throw new Error(`Format ${format.formatid} has a familyid ${format.familyid} that isn't pressent in FAMILY_MATCH_ORDER`);

			if(format.familyid!==familyid)
				continue;
				
			// skip this format if any of our detections are forbidden magic values or our input filename has a forbidden extension
			if(detections.some(detection => ((format.forbiddenMagic || []).some(fm => flexMatch(detection.value, fm)) || (format.forbiddenExt || []).some(fext => f.input.base.toLowerCase().endsWith(fext)))))
			{
				xlog.debug`Excluding format ${formatid} due to forbiddenMagic or forbiddenExt`;
				continue;
			}

			// some formats perform an additional byte check to ensure the file is correct
			if(format.byteCheck)
			{
				let match=true;
				for(const byteCheck of Array.force(format.byteCheck))
				{
					if(byteCheck.ext && byteCheck.ext!==inputFile.ext.toLowerCase())
						continue;
						
					for(let loc=byteCheck.offset, i=0;i<byteCheck.match.length;loc++, i++)
					{
						if(byteCheckBuf===null || !Array.force(byteCheck.match[i]).includes(byteCheckBuf[loc]))
						{
							match = false;
							break;
						}
					}

					if(!match)
						break;
				}

				if(!match)
				{
					xlog.debug`Excluding format ${formatid} due to byteCheck not matching.`;
					continue;
				}
			}

			const priority = Object.hasOwn(format, "priority") ? format.priority : format.PRIORITY.STANDARD;
			const extMatch = (format.ext || []).some(ext => f.input.base.toLowerCase().endsWith(ext) || (format.matchPreExt && ext.toLowerCase()===f.input.preExt.toLowerCase()));
			const filenameMatch = (format.filename || []).some(mfn => flexMatch(f.input.base, mfn, true));
			const idMetaMatch = idMetaData && format.idMeta && format.idMeta(idMetaData);

			// check filesize match
			let hasExpectedFileSize = false;
			let fileSizeMatch = false;
			let fileSizeMatchExt = null;
			if(format.fileSize)
			{
				if(Array.isArray(format.fileSize) || typeof format.fileSize==="number")
				{
					fileSizeMatch = Array.force(format.fileSize).includes(f.input.size);
					hasExpectedFileSize = true;
				}
				else if(extMatch)
				{
					// If we've matched an extension, then we have to also match the expected fileSize
					Object.entries(format.fileSize).forEach(([extEntry, sizeEntry]) =>
					{
						if(extEntry.split(",").some(ext => f.input.base.toLowerCase().endsWith(ext)))
						{
							if(!Array.force(sizeEntry).includes("*"))
								hasExpectedFileSize = true;
							if(Array.force(sizeEntry).includes(f.input.size))
								fileSizeMatch = true;
						}
					});
				}
				else
				{
					// Otherwise we can match any of the extensions fileSize
					Object.entries(format.fileSize).forEach(([extEntry, sizeEntry]) =>
					{
						if(Array.force(sizeEntry).includes(f.input.size))
						{
							fileSizeMatch = true;
							fileSizeMatchExt = extEntry.split(",")[0];
						}
					});
				}
			}

			const weakMagicMatchesHard = [];
			const weakMagicMatchesSoft = [];
			const strongMagicMatches = [];
			for(const d of detections)
			{
				if(!d?.value)
					continue;

				for(const m of (format.magic || []))
				{
					if(!flexMatch(d.value, m))
						continue;

					if((Array.isArray(format.weakMagic) && format.weakMagic.some(weakMagic => flexMatch(d.value, weakMagic))) || (format.weakMagicSensitive && d.weak))
						weakMagicMatchesHard.push(d);
					else if(d.weak)
						weakMagicMatchesSoft.push(d);
					else
						strongMagicMatches.push(d);
				}
			}
			const magicMatch = weakMagicMatchesHard.length || weakMagicMatchesSoft.length || strongMagicMatches.length;
			let weakMatch = false;
			if(!strongMagicMatches.length && (weakMagicMatchesSoft.length || weakMagicMatchesHard.length))
				weakMatch = true;

			if((format.weakFileSize || []).includes(f.input.size))
				weakMatch = true;

			let customMatch = false;
			if(format.customMatch)
				customMatch = await format.customMatch({inputFile, detections, otherFiles, otherDirs, xlog});

			const hasAnyMatch = (extMatch || filenameMatch || idMetaMatch || fileSizeMatch || magicMatch || customMatch);

			const baseMatch = {family : format.family, formatid, priority, extensions : format.ext, magic : format.name};
			if(format.website)
				baseMatch.website = format.website;

			// some formats require some sort of other check to ensure the file is valid
			if(format.idCheck && hasAnyMatch && !(await format.idCheck(inputFile, detections, {extMatch, filenameMatch, idMetaMatch, fileSizeMatch, magicMatch, xlog})))
			{
				xlog.debug`Excluding format ${formatid} due to idCheck not succeeding.`;
				continue;
			}

			// some formats require additional files or directories that may be used
			let auxFiles = null;
			if(format.auxFiles && hasAnyMatch)
			{
				auxFiles = await format.auxFiles(f.input, otherFiles, otherDirs, {fileSizeMatchExt, xlog});

				// If the filesRequired function returns false, then we don't have any required files
				// If it returns an empty array then we fail to match
				if(auxFiles!==false && auxFiles.length===0)
				{
					xlog.debug`Excluding format ${formatid} due to requiredFiles not being present.`;
					continue;
				}

				if(auxFiles && Array.isArray(auxFiles) && auxFiles.length && xlog.atLeast("debug"))
					xlog.debug`Identified auxFiles for ${formatid}:\n\t${auxFiles.map(v => v.base).join("\n\t")}`;
			}
			if(auxFiles)
				baseMatch.auxFiles = auxFiles;
			["charSet", "confidenceAdjust", "website", "mimeType", "fallback"].forEach(key =>
			{
				if(format[key])
					baseMatch[key] = format[key];
			});

			["trustMagic", "unsupported", "untouched"].forEach(key =>
			{
				if(format[key])
					baseMatch[key] = true;
			});

			if(weakMatch)
				baseMatch.weak = true;
			if(fileSizeMatch)
				baseMatch.matchesFileSize = true;
			if(filenameMatch)
				baseMatch.matchesFilename = true;
			if(idMetaMatch)
				baseMatch.matchesIdMeta = true;
			if(customMatch)
				baseMatch.matchesCustom = true;

			const hasWeakExt = format.weakExt===true || (Array.isArray(format.weakExt) && format.weakExt.some(ext => f.input.base.toLowerCase().endsWith(ext)));
			const hasWeakFilename = format.weakFilename===true;
			const hasWeakMagic = format.weakMagic===true || (weakMagicMatchesHard.length && !strongMagicMatches.length);
			//if(["dmg"].includes(format.formatid))
			//	xlog.info`${format.formatid}: ${{weakMatch, weakMagicMatchesHard, weakMagicMatchesSoft, strongMagicMatches, magicMatch, hasWeakMagic, hasWeakExt, hasWeakFilename, extMatch, filenameMatch, idMetaMatch, fileSizeMatch, customMatch}}  format.weakMagic: ${format.weakMagic}`;

			// Non-weak magic matches start at confidence 100.
			if(magicMatch && (!hasWeakMagic || extMatch || filenameMatch || idMetaMatch || fileSizeMatch || customMatch) && !(hasWeakExt && hasWeakMagic) && !format.forbidMagicMatch)
			{
				// Original confidence is a sub-sorter used before assigning proper confidence
				let originalConfidence = 0;
				detections.forEach(detection => (format.magic || []).forEach(m =>
				{
					if(detection.from==="trid" && flexMatch(detection.value, m))
						originalConfidence = Math.max(originalConfidence, detection.confidence);
				}));

				familyMatches.magic.push({...baseMatch, matchType : "magic", extMatch, idMetaMatch, filenameMatch, originalConfidence, hasWeakMagic});
			}

			// metaMatch matches start at confidence 100 as well
			if(idMetaMatch)
				familyMatches.idMeta.push({...baseMatch, matchType : "idMeta", extMatch, hasWeakMagic});

			// customMatch matches also start at confidence 100
			if(customMatch)
				familyMatches.custom.push({...baseMatch, matchType : "custom", extMatch, hasWeakMagic});

			// Extension matches start at confidence 66 (but if we have an expected fileSize we must also match magic or fileSize)
			if(extMatch && (!format.forbidExtMatch || (Array.isArray(format.forbidExtMatch) && !format.forbidExtMatch.some(ext => f.input.base.toLowerCase().endsWith(ext)))) && (!hasExpectedFileSize || magicMatch || fileSizeMatch || idMetaMatch) && !(hasWeakExt && hasWeakMagic))
			{
				const extFamilyMatch = {...baseMatch, matchType : "ext", matchesMagic : magicMatch, hasWeakMagic};
				if(format.magic)
					extFamilyMatch.hasMagic = format.magic;
				familyMatches.ext.push(extFamilyMatch);
			}

			// Filename matches start at confidence 44.
			if(filenameMatch && (!hasWeakFilename || extMatch || fileSizeMatch || magicMatch || idMetaMatch || customMatch))
				familyMatches.filename.push({...baseMatch, matchType : "filename", hasWeakMagic});

			// fileSize matches start at confidence 20.
			if(fileSizeMatch && format.matchFileSize)
			{
				const m = {...baseMatch, matchType : "fileSize"};
				if(fileSizeMatchExt)
					m.fileSizeMatchExt = fileSizeMatchExt;
				if((format.ext || []).some(ext => f.input.base.toLowerCase().endsWith(ext)))
					m.matchesExt = true;

				familyMatches.fileSize.push(m);
			}
		}

		const fallbackMatches = Object.values(familyMatches).flat().filter(m => m.fallback);
		fallbackMatches.forEach(m => { m.matchType = "fallback"; });
		Object.keys(familyMatches).forEach(matchType => { familyMatches[matchType] = familyMatches[matchType].filter(m => !m.fallback); });
		const seenFallbackFormats = new Set();
		familyMatches.fallback = fallbackMatches.filter(({formatid}) =>
		{
			if(!formatid)
				return true;

			if(seenFallbackFormats.has(formatid))
				return false;

			seenFallbackFormats.add(formatid);
			return true;
		});

		[["magic", 100], ["idMeta", 100], ["custom", 100], ["ext", 66], ["filename", 44], ["fileSize", 20], ["fallback", 1]].forEach(([matchType, startConfidence]) =>
		{
			// ext matches that have a magic, but doesn't match the magic should be prioritized lower than ext matches that don't have magic
			// Also ext matches that also match the expected fileSize should be prioritized higher
			if(matchType==="ext")
				familyMatches[matchType].sortMulti([m => m.priority, m => (m.matchesFileSize ? 0 : 1), m => ((m.hasMagic && !m.matchesMagic) ? 1 : 0), m => (m.matchesFilename ? 0 : 1), m => (m.hasWeakMagic ? 1 : 0)]);
			else if(matchType==="magic")
				familyMatches[matchType].sortMulti([m => m.priority, m => (m.extMatch ? 0 : 1), m => m.originalConfidence, m => (m.matchesFileSize ? 0 : 1), m => (m.matchesFilename ? 0 : 1), m => (m.hasWeakMagic ? 1 : 0)], [false, false, true, false, false]);
			else
				familyMatches[matchType].sortMulti([m => m.priority, m => (m.extMatch ? 0 : 1), m => (m.hasWeakMagic ? 1 : 0)]);

			for(const m of familyMatches[matchType])
			{
				if(m.unsupported)
					m.confidence = 1 + (m.matchesExt ? 1 : 0);
				else if(m.weak && !m.trustMagic && !m.extMatch && !m.idMetaMatch && !m.filenameMatch)
					m.confidence = 10;
				else
					m.confidence = Math.max(startConfidence, 0);	// I used to reduce confidence by 1 per additional match in the same type, but since we sort on confidence first (before family) this causes problems (for example archive/moleBoxPacked/erotic_poker.exe should always process as archive/moleBoxPacked before executable/exe when confidence is 100)

				//delete m.priority;
				delete m.originalConfidence;
				
				if(m.confidenceAdjust)
				{
					m.confidence += m.confidenceAdjust(f.input, matchType, m.confidence, {detections});
					m.confidence = Math.max(m.confidence, 1);
					delete m.confidenceAdjust;
				}

				matchesByFamily[matchType].push(m);
			}
		});
	}

	const matches = [...matchesByFamily.magic,
		...matchesByFamily.idMeta.filter(em => !Array.from(matchesByFamily.magic).some(mm => mm.magic===em.magic)),
		...matchesByFamily.custom.filter(em => ![...matchesByFamily.idMeta, ...matchesByFamily.magic].some(mm => mm.magic===em.magic)),
		...matchesByFamily.ext.filter(em => ![...matchesByFamily.custom, ...matchesByFamily.idMeta, ...matchesByFamily.magic].some(mm => mm.magic===em.magic)),
		...matchesByFamily.filename.filter(em => ![...matchesByFamily.ext, ...matchesByFamily.custom, ...matchesByFamily.idMeta, ...matchesByFamily.magic].some(mm => mm.magic===em.magic)),
		...matchesByFamily.fileSize.filter(em => ![...matchesByFamily.filename, ...matchesByFamily.ext, ...matchesByFamily.custom, ...matchesByFamily.idMeta, ...matchesByFamily.magic].some(mm => mm.magic===em.magic))];

	// Stick any fallback matches>=10 here first, before we sort
	matches.push(...matchesByFamily.fallback.filter(id => id.confidence>=10));

	// Now sort by confidence
	// Next, if the confidence is the same, extMatches have a higher priority (so long as the priority of the format is not lower than standard (>2))
	// Finally sort based on family type
	matches.sortMulti([id => (id.confidence || 0), id => (id.extMatch && id.priority<=2 ? 0 : 1), id => FAMILY_MATCH_ORDER.indexOf(id.family.familyid)], [true, false, false]);

	// finally, any fallback matches less than 10 go at the very end
	matches.push(...matchesByFamily.fallback.filter(id => id.confidence<10));

	// Finally we create our return ids. First start out with all 'dexvert' matches
	let ids = matches.map(({family, confidence, magic, extensions, matchType, formatid, unsupported, auxFiles, fileSizeMatchExt, extMatch, website}) => Identification.create({from : "dexvert", confidence, magic, family : family.familyid, formatid, extensions, matchType, unsupported, auxFiles, fileSizeMatchExt, extMatch, website}));

	// Then stick on the 'unknown' format
	// ids.push(Identification.create({from : "dexvert", confidence : 1, magic : "unknown", family : "other", formatid : "unknown", matchType : "fallback"}));

	// Finally add all other detections
	ids = ids.concat(detections.map(({from, confidence, value, extensions, weak}) => Identification.create({from, confidence, magic : value, extensions, weak : !!weak})));

	if(xlog.atLeast("trace"))
	{
		for(const o of ids)
			xlog.trace`RAW MATCH: ${o}`;
	}

	xlog.debug`matches/identifications for ${inputFile.absolute}:\n${ids.map(v => v.pretty("\t")).join("\n")}`;

	return {idMeta : idMetaData, ids};
}

export async function rpcidentify(inputFile, {logLevel="error"}={})
{
	const rpcData = {op : "dexid", inputFilePath : inputFile.absolute, logLevel};
	const {r} = await xu.fetch(`http://${DEXRPC_HOST}:${DEXRPC_PORT}/dex`, {json : rpcData, asJSON : true});
	return r;
}

