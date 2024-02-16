import {xu} from "xu";
import {XLog} from "xlog";
import {fileUtil} from "xutil";
import {formats} from "../src/format/formats.js";
import {FileSet} from "./FileSet.js";
import {DexFile} from "./DexFile.js";
import {Identification} from "./Identification.js";
import {getDetections} from "./Detection.js";

// matches the given value against the matcher. If 'matcher' is a string, then value just needs to start with matcher, unless fullStringMatch is set then the entire string must be a case insensitive match. If 'matcher' is a regexp, it must regex match value.
function flexMatch(value, matcher, fullStringMatch)
{
	return ((typeof matcher==="string" && (fullStringMatch ? (value.toLowerCase()===matcher.toLowerCase()) : value.toLowerCase().startsWith(matcher.toLowerCase()))) || (matcher instanceof RegExp && value.match(matcher)));
}
export {flexMatch};

// A list of family types. Order is the secondary order they will be matched in the case of multiple 'types' of matches (magic, etc, filename) across multiple categories
const FAMILY_MATCH_ORDER = ["archive", "document", "audio", "music", "video", "image", "poly", "font", "text", "executable", "other"];

export async function identify(inputFileRaw, {xlog : _xlog, logLevel="info"}={})
{
	const xlog = _xlog || new XLog(logLevel);

	const inputFile = inputFileRaw instanceof DexFile ? inputFileRaw : await DexFile.create(inputFileRaw);
	if(inputFile.isDirectory)
		return [Identification.create({from : "dexvert", confidence : 100, magic : "directory", family : "other", formatid : "directory", matchType : "magic", unsupported : true})];

	// if it's a symlink, we're done!
	if(inputFile.isSymlink)
		return [Identification.create({from : "dexvert", confidence : 100, magic : "symlink", family : "other", formatid : "symlink", matchType : "magic", unsupported : true})];

	const f = await FileSet.create(inputFile.root, "input", inputFile);
	const detections = await getDetections(f, {xlog});

	xlog.debug`raw detections:\n${detections.map(v => v?.pretty("\t") || v).join("\n")}`;

	const otherFiles = (await (await fileUtil.tree(f.root, {depth : 1, nodir : true})).parallelMap(async v => await DexFile.create(v))).filter(file => !!file && file.absolute!==f.input.absolute);
	const otherDirs = (await (await fileUtil.tree(f.root, {depth : 1, nofile : true})).parallelMap(async v => await DexFile.create(v))).filter(file => !!file);

	// find the largest byteChecks check and read that many bytes in
	const byteCheckMaxSize = Object.values(formats).flatMap(format => Array.force(format.byteCheck || [])).map(byteCheck => byteCheck.offset+byteCheck.match.length).max();
	const byteCheckBuf = await fileUtil.readFileBytes(f.input.absolute, byteCheckMaxSize);

	const matchesByFamily = {magic : [], ext : [], filename : [], fileSize : [], fallback : []};
	for(const familyid of FAMILY_MATCH_ORDER)
	{
		const familyMatches = {magic : [], ext : [], filename : [], fileSize : [], fallback : []};
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
				const magicMatched = flexMatch(detection.value, m);
				if(magicMatched && detection.weak)
					weakMatch = true;

				return magicMatched;
			}));

			const hasAnyMatch = (extMatch || filenameMatch || fileSizeMatch || magicMatch);

			const baseMatch = {family : format.family, formatid, priority, extensions : format.ext, magic : format.name};
			if(format.website)
				baseMatch.website = format.website;

			// some formats require some sort of other check to ensure the file is valid
			if(format.idCheck && hasAnyMatch && !(await format.idCheck(inputFile, detections, {extMatch, filenameMatch, fileSizeMatch, magicMatch})))
			{
				xlog.debug`Excluding format ${formatid} due to idCheck not succeeding.`;
				continue;
			}

			// some formats require additional files or directories that may be used
			let auxFiles = null;
			if(format.auxFiles && (otherFiles.length>0 || otherDirs.length>0) && hasAnyMatch)
			{
				auxFiles = await format.auxFiles(f.input, otherFiles, otherDirs, fileSizeMatchExt);

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

			const trustedMagic = (format.magic || []).filter(m => !(Array.isArray(format.weakMagic) ? format.weakMagic : []).some(wm => m.toString()===wm.toString()));
			const hasWeakExt = format.weakExt===true || (Array.isArray(format.weakExt) && format.weakExt.some(ext => f.input.base.toLowerCase().endsWith(ext)));
			const hasWeakMagic = format.weakMagic===true || (Array.isArray(format.weakMagic) && detections.some(r => format.weakMagic.some(m => flexMatch(r.value, m))) && !detections.some(r => trustedMagic.some(m => flexMatch(r.value, m))));
			const hasWeakFilename = format.weakFilename===true;

			// Non-weak magic matches start at confidence 100.
			if(magicMatch && (!hasWeakMagic || extMatch || filenameMatch || fileSizeMatch) && !(hasWeakExt && hasWeakMagic) && !format.forbidMagicMatch)
			{
				// Original confidence is a sub-sorter used before assigning proper confidence
				let originalConfidence = 0;
				detections.forEach(detection => (format.magic || []).forEach(m =>
				{
					if(detection.from==="trid" && flexMatch(detection.value, m))
						originalConfidence = Math.max(originalConfidence, detection.confidence);
				}));

				familyMatches.magic.push({...baseMatch, matchType : "magic", extMatch, originalConfidence, hasWeakMagic});
			}

			// Extension matches start at confidence 66 (but if we have an expected fileSize we must also match magic or fileSize)
			if(extMatch && (!format.forbidExtMatch || (Array.isArray(format.forbidExtMatch) && !format.forbidExtMatch.some(ext => f.input.base.toLowerCase().endsWith(ext)))) && (!hasExpectedFileSize || magicMatch || fileSizeMatch) && !(hasWeakExt && hasWeakMagic))
			{
				const extFamilyMatch = {...baseMatch, matchType : "ext", matchesMagic : magicMatch, hasWeakMagic};
				if(format.magic)
					extFamilyMatch.hasMagic = format.magic;
				familyMatches.ext.push(extFamilyMatch);
			}

			// Filename matches start at confidence 44.
			if(filenameMatch && (!hasWeakFilename || extMatch || fileSizeMatch || magicMatch))
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

		[["magic", 100], ["ext", 66], ["filename", 44], ["fileSize", 20], ["fallback", 1]].forEach(([matchType, startConfidence]) =>
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
				delete m.priority;
				delete m.originalConfidence;

				if(m.weak && !m.trustMagic && !m.extMatch)
					m.confidence = 10;
				
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
		...matchesByFamily.ext.filter(em => !matchesByFamily.magic.some(mm => mm.magic===em.magic)),
		...matchesByFamily.filename.filter(em => ![...matchesByFamily.ext, ...matchesByFamily.magic].some(mm => mm.magic===em.magic)),
		...matchesByFamily.fileSize.filter(em => ![...matchesByFamily.filename, ...matchesByFamily.ext, ...matchesByFamily.magic].some(mm => mm.magic===em.magic))];

	// Unsupported matches haven't gone through enough testing to warrant any additional confidence than 1
	matches.forEach(match =>
	{
		if(match.unsupported)
			match.confidence = 1 + (match.matchesExt ? 1 : 0);
	});

	// Stick any fallback matches>=10 here first, before we sort
	matches.push(...matchesByFamily.fallback.filter(id => id.confidence>=10));

	// Now sort by confidence
	// Next, if the confidence is the same, extMatches have a higher priority
	// Finally sort based on family type
	matches.sortMulti([id => (id.confidence || 0), id => (id.extMatch ? 0 : 1), id => FAMILY_MATCH_ORDER.indexOf(id.family)], [true, false, false]);

	// finally, any fallback matches less than 10 go at the very end
	matches.push(...matchesByFamily.fallback.filter(id => id.confidence<10));

	// Here we stick the 'dexvert' matches ahead of other 'detections'
	const result = [
		...matches.map(({family, confidence, magic, extensions, matchType, formatid, unsupported, auxFiles, fileSizeMatchExt, website}) => Identification.create({from : "dexvert", confidence, magic, family : family.familyid, formatid, extensions, matchType, unsupported, auxFiles, fileSizeMatchExt, website})),
		...detections.map(({from, confidence, value, extensions, weak}) => Identification.create({from, confidence, magic : value, extensions, weak : !!weak}))
	];

	xlog.debug`matches/identifications for ${inputFile.absolute}:\n${result.map(v => v.pretty("\t")).join("\n")}`;

	return result;
}
