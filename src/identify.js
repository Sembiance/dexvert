import {xu} from "xu";
import {XLog} from "xlog";
import {fileUtil, encodeUtil} from "xutil";
import {RUNTIME} from "./Program.js";
import {formats} from "./format/formats.js";
import {FileSet} from "./FileSet.js";
import {DexFile} from "./DexFile.js";
import {Identification} from "./Identification.js";
import {getDetections} from "./Detection.js";
import {DEXRPC_HOST, DEXRPC_PORT} from "./server/dexrpc.js";

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

	const suspectForkSizes = (dataForkLength+resourceForkLength+128)>inputFile.size || (dataForkLength+128+resourceForkLength+128+128)<inputFile.size;	// later half extra 128's are to align on 128 byte boundaries

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
			return debug ? `${type} date (${v} mac: ${dateMacYear} unix: ${dateUnixYear}) is out of range` : false;
		
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

	// the 16-bit CRC value at offset 124 is a 16-bit CRC-CCITT (XMODEM) of the first 124 bytes of the header
	// this works for most files, but I've encountered too many files where the CRC isn't correct, likely was calculated incorrectly or used an incorrect algo, so we just skip this check entirely for now
	//const crcValue = header.getUInt16BE(124);
	//if(crcValue!==0 && crcValue!==await hashUtil.hashData("CRC-16/XMODEM", header.subarray(0, 124)))
	//	return debug ? `Header CRC (${crcValue}) mismatch` : false;

	// check to see if we have too many 'suspect' things (2 or more) and return false in that case (image/paintPro/AGIGATE.RSC)
	if([suspectForkSizes, suspectFileType || suspectFileCreator, suspectDateDifference || suspectDates.Creation || suspectDates.Modified].filter(Boolean).length>=2)
		return debug ? `Too many suspect parts: suspectForkSizes:${suspectForkSizes} suspectFileType:${suspectFileType} suspectFileCreator:${suspectFileCreator} suspectDates:${Object.entries(suspectDates).map(([k, v]) => `suspectDates.${k}:${v}`).join(", ")} suspectDateDifference:${suspectDateDifference}` : false;

	const region = RUNTIME.globalFlags?.osHint?.macintoshjp ? "japan" : "roman";
	return { macFileType : await encodeUtil.decodeMacintosh({data : fileTypeData, region}), macFileCreator : await encodeUtil.decodeMacintosh({data : fileCreatorData, region})};
}
export {getMacBinaryMeta};

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
	const byteCheckBuf = await fileUtil.readFileBytes(f.input.absolute, byteCheckMaxSize);

	const idMetaData = await getIdMeta(inputFile);
	xlog.debug`idMetaData for ${inputFile.absolute}:\n${idMetaData}`;

	const matchesByFamily = {magic : [], ext : [], filename : [], fileSize : [], idMeta : [], fallback : []};
	for(const familyid of FAMILY_MATCH_ORDER)
	{
		const familyMatches = {magic : [], ext : [], filename : [], fileSize : [], idMeta : [], fallback : []};
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
						if(!Array.force(byteCheck.match[i]).includes(byteCheckBuf[loc]))
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
					hasExpectedFileSize = true;
					fileSizeMatch = Array.force(format.fileSize).includes(f.input.size);
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

			let weakMatch = false;
			const magicMatch = detections.some(detection => (format.magic || []).some(m =>
			{
				if(!detection?.value)
					return false;
				
				const magicMatched = flexMatch(detection.value, m);
				if(magicMatched && detection.weak)
					weakMatch = true;

				return magicMatched;
			}));

			if((format.weakFileSize || []).includes(f.input.size))
				weakMatch = true;

			const hasAnyMatch = (extMatch || filenameMatch || idMetaMatch || fileSizeMatch || magicMatch);

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

			const trustedMagic = (format.magic || []).filter(m => !(Array.isArray(format.weakMagic) ? format.weakMagic : []).some(wm => m.toString()===wm.toString()));
			const hasWeakExt = format.weakExt===true || (Array.isArray(format.weakExt) && format.weakExt.some(ext => f.input.base.toLowerCase().endsWith(ext)));
			const hasWeakMagic = format.weakMagic===true || (Array.isArray(format.weakMagic) && detections.some(r => format.weakMagic.some(m => flexMatch(r.value, m))) && !detections.some(r => trustedMagic.some(m => flexMatch(r.value, m))));
			const hasWeakFilename = format.weakFilename===true;

			// Non-weak magic matches start at confidence 100.
			if(magicMatch && (!hasWeakMagic || extMatch || filenameMatch || idMetaMatch || fileSizeMatch) && !(hasWeakExt && hasWeakMagic) && !format.forbidMagicMatch)
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

			// Extension matches start at confidence 66 (but if we have an expected fileSize we must also match magic or fileSize)
			if(extMatch && (!format.forbidExtMatch || (Array.isArray(format.forbidExtMatch) && !format.forbidExtMatch.some(ext => f.input.base.toLowerCase().endsWith(ext)))) && (!hasExpectedFileSize || magicMatch || fileSizeMatch || idMetaMatch) && !(hasWeakExt && hasWeakMagic))
			{
				const extFamilyMatch = {...baseMatch, matchType : "ext", matchesMagic : magicMatch, hasWeakMagic};
				if(format.magic)
					extFamilyMatch.hasMagic = format.magic;
				familyMatches.ext.push(extFamilyMatch);
			}

			// Filename matches start at confidence 44.
			if(filenameMatch && (!hasWeakFilename || extMatch || fileSizeMatch || magicMatch || idMetaMatch))
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

		[["magic", 100], ["idMeta", 100], ["ext", 66], ["filename", 44], ["fileSize", 20], ["fallback", 1]].forEach(([matchType, startConfidence]) =>
		{
			// ext matches that have a magic, but doesn't match the magic should be prioritized lower than ext matches that don't have magic
			// Also ext matches that also match the expected fileSize should be prioritized higher
			if(matchType==="ext")
				familyMatches[matchType].sortMulti([m => m.priority, m => (m.matchesFileSize ? 0 : 1), m => ((m.hasMagic && !m.matchesMagic) ? 1 : 0), m => (m.matchesFilename ? 0 : 1), m => (m.hasWeakMagic ? 1 : 0)]);
			else if(matchType==="magic")
				familyMatches[matchType].sortMulti([m => m.priority, m => (m.extMatch ? 0 : 1), m => m.originalConfidence, m => (m.matchesFileSize ? 0 : 1), m => (m.matchesFilename ? 0 : 1), m => (m.hasWeakMagic ? 1 : 0)], [false, false, true, false, false]);
			else
				familyMatches[matchType].sortMulti([m => m.priority, m => (m.extMatch ? 0 : 1), m => (m.hasWeakMagic ? 1 : 0)]);

			familyMatches[matchType].forEach((m, i) =>
			{
				m.confidence = Math.max(startConfidence-i, 0);
				//delete m.priority;
				delete m.originalConfidence;

				if(m.weak && !m.trustMagic && !m.extMatch && !m.idMetaMatch && !m.filenameMatch)
				{
					xlog.trace`Reducing confidence of weak match ${m} to 10`;
					m.confidence = 10;
				}
				
				if(m.confidenceAdjust)
				{
					m.confidence += m.confidenceAdjust(f.input, matchType, m.confidence, {detections});
					m.confidence = Math.max(m.confidence, 1);
					delete m.confidenceAdjust;
				}

				matchesByFamily[matchType].push(m);
			});
		});
	}

	const matches = [...matchesByFamily.magic,
		...matchesByFamily.idMeta.filter(em => !Array.from(matchesByFamily.magic).some(mm => mm.magic===em.magic)),
		...matchesByFamily.ext.filter(em => ![...matchesByFamily.idMeta, ...matchesByFamily.magic].some(mm => mm.magic===em.magic)),
		...matchesByFamily.filename.filter(em => ![...matchesByFamily.ext, ...matchesByFamily.idMeta, ...matchesByFamily.magic].some(mm => mm.magic===em.magic)),
		...matchesByFamily.fileSize.filter(em => ![...matchesByFamily.filename, ...matchesByFamily.ext, ...matchesByFamily.idMeta, ...matchesByFamily.magic].some(mm => mm.magic===em.magic))];

	// Unsupported matches haven't gone through enough testing to warrant any additional confidence than 1
	matches.forEach(match =>
	{
		if(match.unsupported)
			match.confidence = 1 + (match.matchesExt ? 1 : 0);
	});

	// Stick any fallback matches>=10 here first, before we sort
	matches.push(...matchesByFamily.fallback.filter(id => id.confidence>=10));

	// Now sort by confidence
	// Next, if the confidence is the same, extMatches have a higher priority (so long as the priority of the format is not lower than standard (>2))
	// Finally sort based on family type
	matches.sortMulti([id => (id.confidence || 0), id => (id.extMatch && id.priority<=2 ? 0 : 1), id => FAMILY_MATCH_ORDER.indexOf(id.family.familyid)], [true, false, false]);

	// finally, any fallback matches less than 10 go at the very end
	matches.push(...matchesByFamily.fallback.filter(id => id.confidence<10));

	// Here we stick the 'dexvert' matches ahead of other 'detections'
	const result = [
		...matches.map(({family, confidence, magic, extensions, matchType, formatid, unsupported, auxFiles, fileSizeMatchExt, website}) => Identification.create({from : "dexvert", confidence, magic, family : family.familyid, formatid, extensions, matchType, unsupported, auxFiles, fileSizeMatchExt, website})),
		...detections.map(({from, confidence, value, extensions, weak}) => Identification.create({from, confidence, magic : value, extensions, weak : !!weak}))
	];

	xlog.debug`matches/identifications for ${inputFile.absolute}:\n${result.map(v => v.pretty("\t")).join("\n")}`;

	return {idMeta : idMetaData, ids : result};
}

export async function rpcidentify(inputFile, {logLevel="error"}={})
{
	const rpcData = {op : "dexid", inputFilePath : inputFile.absolute, logLevel};
	const {r} = await xu.tryFallbackAsync(async () => (await (await fetch(`http://${DEXRPC_HOST}:${DEXRPC_PORT}/dex`, {method : "POST", headers : { "content-type" : "application/json" }, body : JSON.stringify(rpcData)}))?.json()), {});
	return r;
}

