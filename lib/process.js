"use strict";

const tiptoe = require("tiptoe");

const XU = require("@sembiance/xu"),
	path = require("path"),
	fs = require("fs"),
	dexUtil = require(path.join(__dirname, "dexUtil.js")),
	fileUtil = require("@sembiance/xutil").file,
	printUtil = require("@sembiance/xutil").print;

// Returns true if we should continue checking the next identification
function checkShouldContinue(state)
{
	if(state.processed)
	{
		if(state.verbose>=1)
			XU.log`Processing ${XU.c.fg.green + "succeeded"} with format: ${state.id.family}/${state.id.formatid}`;
		
		if(state.keepGoing && state.ids.length>0)
			return true;
		
		return false;
	}

	if(state.ids.length===0 || state.unsupported)
	{
		if(state.verbose>=1)
			XU.log`\nNo more formats to check.`;

		return false;
	}

	return true;
}

// List of steps to perform for processing
exports.steps = function steps(state, p)
{
	return [
		p.util.file.glob(state.output.absolute, "**", {nodir : true}, existingOutputFiles => existingOutputFiles.length===0, `Output directory ${state.output.absolute} is not empty`),
		...p.identify.steps(state, p),
		exports.checkIdentification,
		p.util.flow.batchRepeatUntil([
			exports.processNext,
			p.util.file.findValidOutputFiles(),
			exports.updateProcessed,
			exports.cleanup], checkShouldContinue)
	];
};

// Will come up with a list of ids to check based on the results of the p.identify call
exports.checkIdentification = function checkIdentification(state, {DexvertError, formats}, cb)
{
	const unsupportedIdentifications = state.identify.filter(id => id.from==="dexvert" && id.unsupported);

	// Note, we don't reverse sort these because we pop the next id to perform from the end of the list rather than the beginning
	state.ids = state.identify.filter(id => id.from==="dexvert" && !id.unsupported).multiSort(id => id.confidence);
	
	if(state.ids.length===0)
	{
		if(!state.brute)
		{
			if(unsupportedIdentifications.length===0)
				return setImmediate(() => cb(new DexvertError(state, "No supported matches found.")));
			
			state.unsupported = true;
			state.ids = unsupportedIdentifications.multiSort(id => id.confidence);
			state.id = state.ids.pop();
			return setImmediate(cb);
		}
		
		const idBase = {brute : true, from : "dexvert", confidence : 100};
		state.ids = state.brute.flatMap(family => Object.entries(formats[family]).filter(([, f]) => !f.meta.unsupported && !f.meta.bruteUnsafe).map(([formatid, f]) => ({family, formatid, magic : f.meta.name, extensions : f.meta.ext, ...idBase})));
		if(state.ids.length===0)
			return setImmediate(() => cb(new DexvertError(state, "No formats found to brute force.")));
		
		state.preBruteOutputDirPath = state.output.absolute;
	}
	
	if(state.verbose>=1)
		XU.log`Matched ${state.ids.length} formats:\n${printUtil.columnizeObjects(state.ids.slice().reverse())}`;

	setImmediate(cb);
};

// This will actually perform the processing of the next id in line (popped off the end for performance reasons)
exports.processNext = function processNext(state, p, cb)
{
	if(state.unsupported)
		return setImmediate(cb);

	state.id = state.ids.pop();

	if(state.id.brute)
	{
		const bruteOutputDirPath = path.join(state.preBruteOutputDirPath, state.id.family, state.id.formatid);
		fs.mkdirSync(bruteOutputDirPath, {recursive : true});
		dexUtil.setStateOutput(state, bruteOutputDirPath);

		if(state.keepGoing)
			delete state.processed;
	}

	if(state.verbose>=1)
		XU.log`Attempting to process as format: ${state.id.family}/${state.id.formatid}`;

	const format = p.formats[state.id.family][state.id.formatid];
	const family = p.family[state.id.family];

	tiptoe(
		function preSteps()
		{
			[p.util.file.tmpCWDCreate,
			 p.util.file.safeInput(format.meta.safeExt ? format.meta.safeExt(state) : (format.meta.ext ? format.meta.ext[0] : "")),
			 p.util.file.safeOutput,
			 p.util.meta.input].serialForEach((step, subcb) => step(state, p, subcb), this);
		},
		function performFamilySteps()
		{
			family.steps(state, p).serialForEach((step, subcb) => step(state, p, subcb), this);
		},
		function postSteps()
		{
			p.util.file.tmpCWDCleanup(state, p, this);
		},
		cb
	);
};

// Will call the p.family.updateProcessed method which will set processed to true if the processing was successful
// We can't put this directly into exports.steps above because state.id.family isn't set until this function is actually called
exports.updateProcessed = function updateProcessed(state, p, cb)
{
	if(state.unsupported)
		return setImmediate(cb);

	p.family[state.id.family].updateProcessed(state, p, cb);
};

// Called at the end of each processNext batch
exports.cleanup = function cleanup(state, p, cb)
{
	if(state.unsupported)
		return setImmediate(cb);

	// If we are brute forcing and were not successful, we need to delete the directory we created
	if(state.id.brute && !state.processed)
	{
		delete state.id;
		fileUtil.unlink(state.output.absolute, cb);
		return;
	}

	return setImmediate(cb);
};
