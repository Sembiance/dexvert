"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	fs = require("fs"),
	dexUtil = require(path.join(__dirname, "dexUtil.js")),
	fileUtil = require("@sembiance/xutil").file,
	printUtil = require("@sembiance/xutil").print;

function checkShouldContinue(state)
{
	if(state.processed)
	{
		if(state.verbose>0)
			XU.log`Processing ${XU.c.fg.green + "finished"} with format: ${state.id.family}/${state.id.formatid}`;
		
		return false;
	}

	if(state.ids.length===0)
	{
		if(state.verbose>0)
			XU.log`\nNo more formats to check.`;

		return false;
	}

	return true;
}

exports.steps = function steps(state, p)
{
	return [
		...p.identify.steps(state, p),
		p.util.file.glob(state.output.absolute, "**", {nodir : true}, existingOutputFiles => existingOutputFiles.length===0, `Output directory ${state.output.absolute} is not empty`),
		exports.checkIdentification,
		p.util.flow.batchRepeatUntil([
			exports.processNext,
			p.util.file.findOutputFiles(),
			exports.updateProcessed,
			exports.cleanup], checkShouldContinue)
	];
};

exports.checkIdentification = function checkIdentification(state, {DexvertError, formats}, cb)
{
	state.ids = state.identify.filter(id => id.from==="dexvert" && !id.unsupported).multiSort(id => id.confidence);
	
	if(state.ids.length===0)
	{
		if(!state.brute)
			throw new DexvertError(state, "No supported matches found.");
		
		const idBase = {brute : true, from : "dexvert", confidence : 100};
		state.ids = state.brute.flatMap(family => Object.entries(formats[family]).filter(([, f]) => !f.meta.unsupported).map(([formatid, f]) => ({family, formatid, magic : f.meta.name, extensions : f.meta.ext, ...idBase})));
		if(state.ids.length===0)
			throw new DexvertError(state, "No formats found to brute force.");
		
		state.preBruteOutputDirPath = state.output.absolute;
	}
	
	if(state.verbose>0)
		XU.log`Matched ${state.ids.length} formats:\n${printUtil.columnizeObjects(state.ids.slice().reverse())}`;

	setImmediate(cb);
};

exports.processNext = function processNext(state, p, cb)
{
	state.id = state.ids.pop();

	if(state.id.brute)
	{
		const bruteOutputDirPath = path.join(state.preBruteOutputDirPath, state.id.family, state.id.formatid);
		fs.mkdirSync(bruteOutputDirPath, {recursive : true});
		dexUtil.setStateOutput(state, bruteOutputDirPath);
	}

	if(state.verbose>0)
		XU.log`Attempting to process as format: ${state.id.family}/${state.id.formatid}`;

	const format = p.formats[state.id.family][state.id.formatid];
	const steps = [];
	if(format.steps)
		steps.push(...format.steps(state, p));
	else if(format.meta.program)
		steps.push(...p.util.phase.pre(state, p), p.util.program.run(p.program[format.meta.program]), ...p.util.phase.post(state, p));

	steps.serialForEach((step, stepcb) => step(state, p, stepcb), cb);
};

exports.updateProcessed = function updateProcessed(state, p, cb)
{
	if(state.output.files)
	{
		state.processed = true;
		return setImmediate(cb);
	}

	const format = p.formats[state.id.family][state.id.formatid];
	if(format.updateProcessed)
		return format.updateProcessed(state, p, cb);
	
	setImmediate(cb);
};

// Called by phase.post for each file format it tries
exports.post = function post(state, p, cb)
{
	const format = p.formats[state.id.family][state.id.formatid];
	if(format.post)
		format.post(state, p, cb);
	else
		setImmediate(cb);
};

exports.cleanup = function cleanup(state, p, cb)
{
	if(!state.id.brute || state.processed)
		return setImmediate(cb);
	
	fileUtil.unlink(state.output.absolute, cb);
};
