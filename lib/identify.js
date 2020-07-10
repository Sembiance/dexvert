"use strict";
const XU = require("@sembiance/xu");

exports.steps = function steps({input}, {util, program})
{
	return [
		util.flow.parallel([
			util.file.exists(input.filePath, exists => !!exists, `File ${input.filePath} does not exist`),
			util.file.stat(input.filePath, stat => stat.size>0, `File ${input.filePath} is empty`)
		]),
		util.flow.parallel([util.program.run(program.file), util.program.run(program.trid), util.program.run(program.fido)]),
		exports.identify
	];
};

exports.identify = function identify(state, {C, formats}, cb)
{
	const results = [{magic : state.run.file[0].trim(), from : "file", confidence : 100}];

	const tridMatches = [];
	try
	{
		state.run.trid[0].split("\n").forEach(tridLine =>
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

	const fido = (state.run.fido[0] || "").trim();
	if(fido.length>0)
		results.push({magic : fido, from : "fido", confidence : 100});
	
	const formatMatches = {magic : [], ext : [], filename : []};
	Object.forEach(formats, (formatFamily, formatTypes) =>
	{
		const familyMatches = {magic : [], ext : [], filename : []};
		Object.forEach(formatTypes, (formatid, format) =>
		{
			const meta = format.meta;

			// If any of our results are forbidden, stop now.
			if(results.some(result => (meta.forbiddenMagic || []).some(fm => C.flexMatch(result.magic, fm))))
				return;

			const priority = meta.hasOwnProperty("priority") ? meta.priority : C.PRIORITY.STANDARD;
			const extMatch = !meta.forbidExtMatch && (meta.ext || []).includes(state.input.ext.toLowerCase());
			const filenameMatch = (meta.filename || []).some(mfn => C.flexMatch(state.input.base, mfn, true));
			const magicMatch = results.some(result => (meta.magic || []).some(m => C.flexMatch(result.magic, m)));

			const baseMatch = {from : "dexvert", family : formatFamily, formatid};
			if(meta.unsupported)
				baseMatch.unsupported = true;
			
			// Non-weak magic matches start at confidence 100.
			if(magicMatch && (!meta.weakMagic || extMatch || filenameMatch))
				familyMatches.magic.push({...baseMatch, magic : meta.name, extensions : meta.ext, priority});

			// Extension matches start at confidence 66.
			if(extMatch)
				familyMatches.ext.push({...baseMatch, magic : meta.name, extensions : meta.ext, priority});
			
			// Filename matches start at confidence 33.
			if(filenameMatch)
				familyMatches.filename.push({...baseMatch, magic : meta.name, extensions : meta.ext, priority});
		});

		[["magic", 100], ["ext", 66], ["filename", 33]].forEach(([matchType, startConfidence]) =>
		{
			familyMatches[matchType].multiSort(m => m.priority);
			familyMatches[matchType].forEach((m, i) =>
			{
				m.confidence = startConfidence-i;
				delete m.priority;

				formatMatches[matchType].push(m);
			});
		});
	});

	results.push(...formatMatches.magic,
		...formatMatches.ext.filter(em => !formatMatches.magic.some(mm => mm.magic===em.magic)),
		...formatMatches.filename.filter(em => ![...formatMatches.ext, ...formatMatches.magic].some(mm => mm.magic===em.magic)));
		
	results.multiSort([result => result.from, result => (result.confidence || 0)], [false, true]);

	state.identify = results;

	setImmediate(cb);
};
