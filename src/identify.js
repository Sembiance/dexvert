import {xu} from "xu";
import {fileUtil} from "xutil";
import {Format} from "./Format.js";
import {Program} from "./Program.js";
import {FileSet} from "./FileSet.js";
import {DexFile} from "./DexFile.js";

const TEXT_MAGIC =
[
	"ASCII text", "ISO-8859 text", "UTF-8 Unicode text", "Non-ISO extended-ASCII text", "ReStructuredText file", "International EBCDIC text", "UTF-8 Unicode text", "Printable ASCII", "Unicode text, UTF-8 text",
	"Algol 68 source, ISO-8859 text"	// Algol 68 is often mis-identified, usually confused with Pascal files. Just treat it as regular text
];

// matches the given value against the matcher. If 'matcher' is a string, then value just needs to start with matcher, unless fullStringMatch is set then the entire string must be a case insensitive match. If 'matcher' is a regexp, it must regex match value.
function flexMatch(value, matcher, fullStringMatch)
{
	return ((typeof matcher==="string" && (fullStringMatch ? (value.toLowerCase()===matcher.toLowerCase()) : value.toLowerCase().startsWith(matcher.toLowerCase()))) || (matcher instanceof RegExp && value.match(matcher)));
}

export async function identify(inputFilePath, {verbose})
{
	const input = await FileSet.create(await DexFile.create(inputFilePath));
	const detections = (await Promise.all(["file", "trid", "checkBytes", "dexmagic"].map(programid => Program.runProgram(programid, input, undefined, {verbose})))).flatMap(o => o.meta.detections);

	if(verbose)
		xu.log`raw detections: ${detections.map(({confidence, from, value, extensions, weak}) => ({"%" : confidence, from, value, extensions, weak}))}`;

	await input.addFiles("aux", await fileUtil.tree(input.root, {depth : 1}));

	// results -> detections
	// result.untrustworthy -> detection.weak ==
	// inputFileSize -> input.primary.size
	// meta -> format

	for(const [formatid, format] of Object.entries(await Format.loadFormats()))
	{
		// skip this format if any of our detections are forbidden magic values or our input filename has a forbidden extension
		if(detections.some(detection => ((format.forbiddenMagic || []).some(fm => flexMatch(detection.value, fm)) || (format.forbiddenExt || []).some(fext => input.primary.base.toLowerCase().endsWith(fext)))))
		{
			if(verbose)
				xu.log`Excluding format ${formatid} due to forbiddenMagic or forbiddenExt`;
			continue;
		}

		// skip this format if it's marked as unsafe and our file has been transformed and we don't explictly allow transforming
		if(input.primary.transformed && format.unsafe && !format.allowTransform)
		{
			if(verbose)
				xu.log`Excluding format ${formatid} due to input being a transformed file and the format being marked as unsafe.`;
			continue;
		}
		
		xu.log`${format}`;
		
		/*
		// Some formats have custom checkers that must be satisfied to match
		if(format.idCheck)
		{
			let idCheckSuccess = false;
			try
			{
				idCheckSuccess = format.idCheck(state, results);
			}
			catch(err)
			{
				if(err)
				{
					idCheckSuccess = false;
					if(state.verbose>=1)
						console.error(err);
				}
			}

			if(!idCheckSuccess)
				return;
		}
		
		// Some formats have required files that must be present in the input dir
		if(format.meta.filesRequired)
		{
			const requiredFiles = format.meta.filesRequired(state, state.input.otherFiles);

			// If the filesRequired function returns false, then we don't have any required files
			// If it returns an empty array then we fail
			if(requiredFiles!==false && requiredFiles.length===0)
				return;
		}
		
		let matchIsUntrustworthy = false;
		const priority = meta.hasOwnProperty("priority") ? meta.priority : C.PRIORITY.STANDARD;
		const extMatch = ((!meta.unsupported || format.idCheck) || meta.magic) && (meta.ext || []).some(ext => state.input.base.toLowerCase().endsWith(ext));
		const filenameMatch = (meta.filename || []).some(mfn => dexUtil.flexMatch(state.input.base, mfn, true));
		
		let hasExpectedFileSize = false;
		let fileSizeMatch = false;
		let fileSizeMatchExt = null;
		if(meta.fileSize)
		{
			if(Array.isArray(meta.fileSize) || typeof meta.fileSize==="number")
			{
				hasExpectedFileSize = true;
				fileSizeMatch = Array.force(meta.fileSize).includes(inputFileSize);
			}
			else if(extMatch)
			{
				// If we've matched an extension, then we have to also match the expected fileSize
				Object.entries(meta.fileSize).forEach(([extEntry, sizeEntry]) =>
				{
					if(extEntry.split(",").some(ext => state.input.base.toLowerCase().endsWith(ext)))
					{
						hasExpectedFileSize = true;
						if(Array.force(sizeEntry).includes(inputFileSize))
							fileSizeMatch = true;
					}
				});
			}
			else
			{
				// Otherwise we can match any of the extensions fileSize
				Object.entries(meta.fileSize).forEach(([extEntry, sizeEntry]) =>
				{
					if(Array.force(sizeEntry).includes(inputFileSize))
					{
						fileSizeMatch = true;
						fileSizeMatchExt = extEntry.split(",")[0];
					}
				});
			}
		}

		const magicMatch = results.some(result => (meta.magic || []).some(m =>
		{
			const magicMatched = dexUtil.flexMatch(result.magic, m);
			
			// If this magic is marked as unstrustworthy or the confidence of the match is below 5% (only useful from trid)
			if(magicMatched && (result.untrustworthy || result.confidence<5))
				matchIsUntrustworthy = true;

			return magicMatched;
		}));

		const baseMatch = {from : "dexvert", family : formatFamily, formatid, priority, extensions : meta.ext, magic : meta.name};
		["encoding", "confidenceAdjust", "website", "mimeType", "hljsLang", "fallback"].forEach(key =>
		{
			if(meta[key])
				baseMatch[key] = meta[key];
		});

		["trustMagic", "unsupported", "untouched", "highConfidence"].forEach(key =>
		{
			if(meta[key])
				baseMatch[key] = true;
		});

		if(matchIsUntrustworthy)
			baseMatch.untrustworthy = true;

		const trustedMagic = (meta.magic || []).filter(m => !(Array.isArray(meta.weakMagic) ? meta.weakMagic : []).some(wm => m.toString()===wm.toString()));
		const hasWeakExt = meta.weakExt===true || (Array.isArray(meta.weakExt) && meta.weakExt.some(ext => state.input.base.toLowerCase().endsWith(ext)));
		const hasWeakMagic = meta.weakMagic===true || (Array.isArray(meta.weakMagic) && results.some(r => meta.weakMagic.some(m => dexUtil.flexMatch(r.magic, m))) && !results.some(r => trustedMagic.some(m => dexUtil.flexMatch(r.magic, m))));

		// Non-weak magic matches start at confidence 100.
		if(magicMatch && (!hasWeakMagic || extMatch || filenameMatch || fileSizeMatch) && !(hasWeakExt && hasWeakMagic) && !meta.forbidMagicMatch)
		{
			// Original confidence is a sub-sorter used before assigning proper confidence
			let originalConfidence = 0;
			results.forEach(result => (meta.magic || []).forEach(m =>
			{
				if(result.from==="trid" && dexUtil.flexMatch(result.magic, m))
					originalConfidence = Math.max(originalConfidence, result.confidence);
			}));

			familyMatches.magic.push({...baseMatch, matchType : "magic", extMatch, originalConfidence});
		}

		// Extension matches start at confidence 66 (but if we have an expected fileSize we must also match magic or fileSize)
		if(extMatch && (!meta.forbidExtMatch || (Array.isArray(meta.forbidExtMatch) && !meta.forbidExtMatch.some(ext => state.input.base.toLowerCase().endsWith(ext)))) && (!hasExpectedFileSize || magicMatch || fileSizeMatch) && !(hasWeakExt && hasWeakMagic))
		{
			const extFamilyMatch = {...baseMatch, matchType : "ext", matchesMagic : magicMatch};
			if(fileSizeMatch)
				extFamilyMatch.matchesFileSize = true;
			if(meta.magic)
				extFamilyMatch.hasMagic = meta.magic;
			familyMatches.ext.push(extFamilyMatch);
		}
		
		// Filename matches start at confidence 33.
		if(filenameMatch)
			familyMatches.filename.push({...baseMatch, matchType : "filename"});
		
		// fileSize matches start at confidence 20.
		if(fileSizeMatch && !meta.forbidFileSizeMatch)
		{
			const m = {...baseMatch, matchType : "fileSize"};
			if(fileSizeMatchExt)
				m.fileSizeMatchExt = fileSizeMatchExt;
			if((meta.ext || []).some(ext => state.input.base.toLowerCase().endsWith(ext)))
				m.matchesExt = true;

			familyMatches.fileSize.push(m);
		}
		*/
	}

	

	/*
	const formatMatches = {magic : [], ext : [], filename : [], fileSize : [], fallback : []};
	Object.forEach(formats, (formatFamily, formatTypes) =>
	{
		const familyMatches = {magic : [], ext : [], filename : [], fileSize : [], fallback : []};
		Object.forEach(formatTypes, (formatid, format) =>
		{
			
		});

		const fallbackMatches = Object.values(familyMatches).flat().filter(m => m.fallback);
		fallbackMatches.forEach(m => { m.matchType = "fallback"; });
		Object.keys(familyMatches).forEach(matchType => { familyMatches[matchType] = familyMatches[matchType].filter(m => !m.fallback); });
		familyMatches.fallback = fallbackMatches;

		[["magic", 100], ["ext", 66], ["filename", 33], ["fileSize", 20], ["fallback", 1]].forEach(([matchType, startConfidence]) =>
		{
			////if(matchType==="magic")
			//	console.log(familyMatches[matchType]);
			// ext matches that have a magic, but doesn't match the magic should be prioritized lower than ext matches that don't have magic
			// Also ext matches that also match the expected fileSize should be prioritized higher
			if(matchType==="ext")
				familyMatches[matchType].multiSort([m => m.priority, m => ((m.hasMagic && !m.matchesMagic) ? 1 : 0), m => (m.matchesFileSize ? 0 : 1)]);
			else if(matchType==="magic")
				familyMatches[matchType].multiSort([m => m.priority, m => (m.extMatch ? 0 : 1), m => m.originalConfidence], [false, false, true]);
			else
				familyMatches[matchType].multiSort([m => m.priority, m => (m.extMatch ? 0 : 1)]);

			familyMatches[matchType].forEach((m, i) =>
			{
				m.confidence = Math.max(startConfidence-i, 0);
				delete m.priority;

				if(m.untrustworthy && !m.trustMagic && !m.extMatch)
					m.confidence = 10;
				
				if(m.confidenceAdjust)
				{
					m.confidence += m.confidenceAdjust(state, matchType, m.confidence);
					delete m.confidenceAdjust;
				}

				formatMatches[matchType].push(m);
			});
		});
	});

	results.push(...formatMatches.magic,
		...formatMatches.ext.filter(em => !formatMatches.magic.some(mm => mm.magic===em.magic)),
		...formatMatches.filename.filter(em => ![...formatMatches.ext, ...formatMatches.magic].some(mm => mm.magic===em.magic)),
		...formatMatches.fileSize.filter(em => ![...formatMatches.filename, ...formatMatches.ext, ...formatMatches.magic].some(mm => mm.magic===em.magic)));

	// Unsupported matches haven't gone through enough testing to warrant any additional confidence than 1
	results.forEach(result =>
	{
		if(result.unsupported && !result.highConfidence)
			result.confidence = 1 + (result.matchesExt ? 1 : 0);
	});

	// Now sort by confidence
	// First sort by where it's from, with dexvert being at the top
	// Next by confidence, higher the better
	// Next, if the confidence is the same, extMatches have a higher priority
	// Finally sort based on family type
	results.multiSort([result => ["dexvert", "file", "trid", "dexmagic"].indexOf(result.from), id => (id.confidence || 0), id => (id.extMatch ? 0 : 1), id => C.FAMILIES.indexOf(id.family)], [false, true, false, false]);

	results.push(...formatMatches.fallback);

	state.identify = results;
	*/
}
