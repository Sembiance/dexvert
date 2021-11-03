import {xu} from "xu";
import {fileUtil} from "xutil";
import {Format} from "./Format.js";
import {Program} from "./Program.js";
import {FileSet} from "./FileSet.js";
import {DexFile} from "./DexFile.js";

// matches the given value against the matcher. If 'matcher' is a string, then value just needs to start with matcher, unless fullStringMatch is set then the entire string must be a case insensitive match. If 'matcher' is a regexp, it must regex match value.
function flexMatch(value, matcher, fullStringMatch)
{
	return ((typeof matcher==="string" && (fullStringMatch ? (value.toLowerCase()===matcher.toLowerCase()) : value.toLowerCase().startsWith(matcher.toLowerCase()))) || (matcher instanceof RegExp && value.match(matcher)));
}

// A list of family types. Order is the secondary order they will be matched in the case of multiple 'types' of matches (magic, etc, filename) across multiple categories
// If you add any here, you also need to update retromission.com msdos.styl
const FAMILY_MATCH_ORDER = ["archive", "document", "audio", "music", "video", "image", "3d", "font", "text", "executable", "rom", "other"];

export async function identify(inputFile, {verbose})
{
	const input = await FileSet.create(inputFile);
	const detections = (await Promise.all(["file", "trid", "checkBytes", "dexmagic"].map(programid => Program.runProgram(programid, input, undefined, {verbose})))).flatMap(o => o.meta.detections);

	if(verbose)
		xu.log`raw detections: ${detections.map(({confidence, from, value, extensions, weak}) => ({"%" : confidence, from, value, extensions, weak}))}`;

	const formats = await Format.loadFormats();

	const otherFiles = (await Promise.all((await fileUtil.tree(input.root, {depth : 1, nodir : true})).map(v => DexFile.create(v)))).filter(file => file.absolute!==input.primary.absolute);
	const otherDirs = await Promise.all((await fileUtil.tree(input.root, {depth : 1, nofile : true})).map(v => DexFile.create(v)));

	// find the largest byteChecks check and read that many bytes in
	const byteCheckMaxSize = Object.values(formats).flatMap(format => (typeof format.byteCheck==="function" ? Array.force(format.byteCheck(input)) : Array.force(format.byteCheck || []))).map(byteCheck => byteCheck.offset+byteCheck.match.length).max();
	const byteCheckBuf = await fileUtil.readFileBytes(input.primary.absolute, byteCheckMaxSize);

	const matchesByFamily = {magic : [], ext : [], filename : [], fileSize : [], fallback : []};
	FAMILY_MATCH_ORDER.forEach(familyid =>
	{
		const familyMatches = {magic : [], ext : [], filename : [], fileSize : [], fallback : []};
		for(const [formatid, format] of Object.entries(formats))
		{
			if(format.familyid!==familyid)
				continue;

			// skip this format if any of our detections are forbidden magic values or our input filename has a forbidden extension
			if(detections.some(detection => ((format.forbiddenMagic || []).some(fm => flexMatch(detection.value, fm)) || (format.forbiddenExt || []).some(fext => input.primary.base.toLowerCase().endsWith(fext)))))
			{
				if(verbose)
					xu.log`Excluding format ${formatid} due to forbiddenMagic or forbiddenExt`;
				continue;
			}

			// skip this format if it's marked as unsafe and our file has been transformed and we don't explictly allow transforming
			if(input.primary.transformed && format.transformUnsafe)
			{
				if(verbose)
					xu.log`Excluding format ${formatid} due to input being a transformed file and the format being marked as unsafe.`;
				continue;
			}

			// some formats perform an additional byte check to ensure the file is correct
			if(format.byteCheck)
			{
				const byteChecks = typeof format.byteCheck==="function" ? Array.force(format.byteCheck(input)) : Array.force(format.byteCheck);
				let match=true;
				for(const byteCheck of byteChecks)
				{
					for(let loc=byteCheck.offset, i=0;i<byteCheck.match.length;loc++, i++)
					{
						if(byteCheckBuf[loc]!==byteCheck.match[i])
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
					if(verbose)
						xu.log`Excluding format ${formatid} due to byteCheck not matching.`;
					continue;
				}
			}

			// some formats requrie additional files or directories that may be used
			if(format.auxFiles)
			{
				const auxFiles = format.auxFiles(input.primary, otherFiles, otherDirs);

				// If the filesRequired function returns false, then we don't have any required files
				// If it returns an empty array then we fail to match
				if(auxFiles!==false && auxFiles.length===0)
				{
					if(verbose)
						xu.log`Excluding format ${formatid} due to requiredFiles not being present.`;
					continue;
				}
			}

			const priority = Object.hasOwn(format, "priority") ? format.priority : format.PRIORITY.STANDARD;
			const extMatch = ((!format.unsupported || format.byteCheck) || format.magic) && (format.ext || []).some(ext => input.primary.base.toLowerCase().endsWith(ext));
			const filenameMatch = (format.filename || []).some(mfn => flexMatch(input.primary.base, mfn, true));

			let hasExpectedFileSize = false;
			let fileSizeMatch = false;
			let fileSizeMatchExt = null;
			if(format.fileSize)
			{
				if(Array.isArray(format.fileSize) || typeof format.fileSize==="number")
				{
					hasExpectedFileSize = true;
					fileSizeMatch = Array.force(format.fileSize).includes(input.primary.size);
				}
				else if(extMatch)
				{
					// If we've matched an extension, then we have to also match the expected fileSize
					Object.entries(format.fileSize).forEach(([extEntry, sizeEntry]) =>
					{
						if(extEntry.split(",").some(ext => input.primary.base.toLowerCase().endsWith(ext)))
						{
							hasExpectedFileSize = true;
							if(Array.force(sizeEntry).includes(input.primary.size))
								fileSizeMatch = true;
						}
					});
				}
				else
				{
					// Otherwise we can match any of the extensions fileSize
					Object.entries(format.fileSize).forEach(([extEntry, sizeEntry]) =>
					{
						if(Array.force(sizeEntry).includes(input.primary.size))
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

			const baseMatch = {family : format.family, formatid, priority, extensions : format.ext, magic : format.name};
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

			const trustedMagic = (format.magic || []).filter(m => !(Array.isArray(format.weakMagic) ? format.weakMagic : []).some(wm => m.toString()===wm.toString()));
			const hasWeakExt = format.weakExt===true || (Array.isArray(format.weakExt) && format.weakExt.some(ext => input.primary.base.toLowerCase().endsWith(ext)));
			const hasWeakMagic = format.weakMagic===true || (Array.isArray(format.weakMagic) && detections.some(r => format.weakMagic.some(m => flexMatch(r.value, m))) && !detections.some(r => trustedMagic.some(m => flexMatch(r.value, m))));

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

				familyMatches.magic.push({...baseMatch, matchType : "magic", extMatch, originalConfidence});
			}

			// Extension matches start at confidence 66 (but if we have an expected fileSize we must also match magic or fileSize)
			if(extMatch && (!format.forbidExtMatch || (Array.isArray(format.forbidExtMatch) && !format.forbidExtMatch.some(ext => input.primary.base.toLowerCase().endsWith(ext)))) && (!hasExpectedFileSize || magicMatch || fileSizeMatch) && !(hasWeakExt && hasWeakMagic))
			{
				const extFamilyMatch = {...baseMatch, matchType : "ext", matchesMagic : magicMatch};
				if(fileSizeMatch)
					extFamilyMatch.matchesFileSize = true;
				if(format.magic)
					extFamilyMatch.hasMagic = format.magic;
				familyMatches.ext.push(extFamilyMatch);
			}

			// Filename matches start at confidence 33.
			if(filenameMatch)
				familyMatches.filename.push({...baseMatch, matchType : "filename"});

			// fileSize matches start at confidence 20.
			if(fileSizeMatch && format.allowFileSizeMatch)
			{
				const m = {...baseMatch, matchType : "fileSize"};
				if(fileSizeMatchExt)
					m.fileSizeMatchExt = fileSizeMatchExt;
				if((format.ext || []).some(ext => input.primary.base.toLowerCase().endsWith(ext)))
					m.matchesExt = true;

				familyMatches.fileSize.push(m);
			}

			//xu.log`${{formatid, priority, extMatch, filenameMatch, fileSizeMatch, magicMatch, weakMatch, hasWeakExt, hasWeakMagic}}`;
			//xu.log`${baseMatch}`;
		}

		const fallbackMatches = Object.values(familyMatches).flat().filter(m => m.fallback);
		fallbackMatches.forEach(m => { m.matchType = "fallback"; });
		Object.keys(familyMatches).forEach(matchType => { familyMatches[matchType] = familyMatches[matchType].filter(m => !m.fallback); });
		familyMatches.fallback = fallbackMatches;

		[["magic", 100], ["ext", 66], ["filename", 33], ["fileSize", 20], ["fallback", 1]].forEach(([matchType, startConfidence]) =>
		{
			// ext matches that have a magic, but doesn't match the magic should be prioritized lower than ext matches that don't have magic
			// Also ext matches that also match the expected fileSize should be prioritized higher
			if(matchType==="ext")
				familyMatches[matchType].sortMulti([m => m.priority, m => ((m.hasMagic && !m.matchesMagic) ? 1 : 0), m => (m.matchesFileSize ? 0 : 1)]);
			else if(matchType==="magic")
				familyMatches[matchType].sortMulti([m => m.priority, m => (m.extMatch ? 0 : 1), m => m.originalConfidence], [false, false, true]);
			else
				familyMatches[matchType].sortMulti([m => m.priority, m => (m.extMatch ? 0 : 1)]);

			familyMatches[matchType].forEach((m, i) =>
			{
				m.confidence = Math.max(startConfidence-i, 0);
				delete m.priority;
				delete m.originalConfidence;

				if(m.weak && !m.trustMagic && !m.extMatch)
					m.confidence = 10;
				
				if(m.confidenceAdjust)
				{
					m.confidence += m.confidenceAdjust(input.primary, matchType, m.confidence);
					delete m.confidenceAdjust;
				}

				matchesByFamily[matchType].push(m);
			});
		});
	});

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

	// Now sort by confidence
	// First sort by where it's from, with dexvert being at the top
	// Next by confidence, higher the better
	// Next, if the confidence is the same, extMatches have a higher priority
	// Finally sort based on family type
	matches.sortMulti([id => (id.confidence || 0), id => (id.extMatch ? 0 : 1), id => FAMILY_MATCH_ORDER.indexOf(id.family)], [true, false, false]);

	matches.push(...matchesByFamily.fallback);

	return [
		...matches.map(({family, confidence, magic, extensions, matchType, formatid, unsupported}) => ({from : "dexvert", confidence, magic, family : family.familyid, formatid, extensions, matchType, unsupported})),
		...detections.map(({from, confidence, value, extensions}) => ({from, confidence, magic : value, extensions}))
	];
}
