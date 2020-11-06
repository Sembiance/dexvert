"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	dexUtil = require("./dexUtil.js"),
	program = require("./util/program.js"),
	fs = require("fs");

exports.steps =
[
	(state0, p0) => p0.util.flow.parallel([
		(state, p) => p.util.file.exists(state.input.filePath, exists => !!exists, `File ${state.input.filePath} does not exist`),
		(state, p) => p.util.file.stat(state.input.filePath, stat => stat.size>0, `File ${state.input.filePath} is empty`)
	]),
	(state0, p0) => p0.util.flow.parallel([
		(state, p) => p.util.file.glob(path.dirname(state.input.absolute), "*", {nodir : true}, otherFilePaths => { state.input.otherFiles = otherFilePaths.map(v => path.basename(v)).removeOnce(state.input.base); return true; }),
		() => ({program : "file"}),
		() => ({program : "trid"}),
		() => ({program : "fido"})]),
	() => exports.identify
];

exports.identify = function identify(state, {C, formats}, cb)
{
	const results = [{magic : (program.getRan(state, "file").results || "").trim(), from : "file", confidence : 100}];

	const tridMatches = [];
	try
	{
		(program.getRan(state, "trid").results || "").split("\n").forEach(tridLine =>
		{
			const parts = tridLine.match(/^\s*(?<confidence>\d+\.\d)% \((?<extension>[^)]+)\) (?<magic>.+) \([^)]+\)$/);
			if(!parts)
				return;
			
			const tridMatch = {confidence : +parts.groups.confidence, magic : parts.groups.magic};
			if(parts.groups.extension.includes("/"))
				tridMatch.extensions = parts.groups.extension.split("/").map(ext => (ext.charAt(0)==="." ? "" : ".") + ext);
			else
				tridMatch.extensions = [parts.groups.extension];

			tridMatch.extensions.mapInPlace(ext => ext.toLowerCase());
			tridMatches.push(tridMatch);
		});
	}
	catch(tridErr) { }

	results.push(...tridMatches.map(v => { v.from = "trid"; return v; }));

	const fido = (program.getRan(state, "fido").results || "").trim();
	if(fido.length>0)
		results.push({magic : fido, from : "fido", confidence : 100});
	
	// Mark any magics that are very generic as untrustworthy
	results.forEach(result =>
	{
		if(C.UNTRUSTWORTHY_MAGIC.some(m => dexUtil.flexMatch(result.magic, m)))
			result.untrustworthy = true;
	});

	if(state.verbose>=5)
		console.log("Raw ID results, before filtering", results);
	
	const inputFileSize = fs.statSync(state.input.absolute).size;

	const formatMatches = {magic : [], ext : [], filename : [], fileSize : []};
	Object.forEach(formats, (formatFamily, formatTypes) =>
	{
		const familyMatches = {magic : [], ext : [], filename : [], fileSize : []};
		Object.forEach(formatTypes, (formatid, format) =>
		{
			const meta = format.meta;

			// If any of our results are forbidden, stop now.
			if(results.some(result => (meta.forbiddenMagic || []).some(fm => dexUtil.flexMatch(result.magic, fm))))
			{
				if(state.verbose>=5)
					XU.log`Excluding results due to forbidden magic: ${meta.forbiddenMagic}`;
				return;
			}

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
			["encoding", "confidenceAdjust"].forEach(key =>
			{
				if(meta[key])
					baseMatch[key] = meta[key];
			});

			["trustMagic", "unsupported"].forEach(key =>
			{
				if(meta[key])
					baseMatch[key] = true;
			});

			if(matchIsUntrustworthy)
				baseMatch.untrustworthy = true;

			// Non-weak magic matches start at confidence 100.
			if(magicMatch && (!meta.weakMagic || extMatch || filenameMatch || fileSizeMatch))
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
			if(extMatch && (!meta.forbidExtMatch || (Array.isArray(meta.forbidExtMatch) && !meta.forbidExtMatch.some(ext => state.input.base.toLowerCase().endsWith(ext)))) && (!hasExpectedFileSize || magicMatch || fileSizeMatch))
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
		});

		[["magic", 100], ["ext", 66], ["filename", 33], ["fileSize", 20]].forEach(([matchType, startConfidence]) =>
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
				m.confidence = startConfidence-i;
				delete m.priority;

				if(m.untrustworthy && !m.trustMagic)
					m.confidence = 10;
				
				if(m.confidenceAdjust)
				{
					m.confidence += m.confidenceAdjust(state, matchType);
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
		if(result.unsupported)
			result.confidence = 1 + (result.matchesExt ? 1 : 0);
	});

	// Now sort by confidence
	results.multiSort([result => result.from, result => (result.extMatch ? 0 : 1), result => (result.confidence || 0)], [false, false, true]);

	state.identify = results;

	setImmediate(cb);
};
