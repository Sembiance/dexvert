"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	fs = require("fs"),
	tiptoe = require("tiptoe"),
	C = require("./C.js"),
	dexUtil = require("./dexUtil.js"),
	fileUtil = require("@sembiance/xutil").file,
	printUtil = require("@sembiance/xutil").print;

// Returns true if we should continue checking the next identification
function checkShouldContinue(state)
{
	if(state.processed)
	{
		if(state.verbose>=1)
			XU.log`Processing ${`${XU.c.fg.green}succeeded`} with format: ${state.id.family}/${state.id.formatid}`;
		
		if(state.keepGoing && state.ids.length>0)
			return true;
		
		return false;
	}

	if(state.ids.length===0 || state.unsupported)
	{
		if(state.verbose>=1)
			XU.log`\nNo more formats to check.`;

		if(!state.unsupported)
			setFallthroughID(state);

		return false;
	}

	return true;
}

// List of steps to perform for processing
exports.steps =
[
	(state, p) => p.util.file.glob(state.output.absolute, "**", {nodir : true}, existingOutputFiles => existingOutputFiles.length===0, `Output directory ${state.output.absolute} is not empty`),
	(state, p) => p.util.flow.serial(p.identify.steps),
	() => exports.checkIdentification,
	(state0, p0) => p0.util.flow.batchRepeatUntil([
		() => exports.processNext,
		(state, p) => p.util.file.findValidOutputFiles(true),
		() => exports.updateProcessed,
		() => exports.cleanup], checkShouldContinue)
];

function setFallthroughID(state)
{
	delete state.id;

	const unsupportedIdentifications = state.identify.filter(id => id.from==="dexvert" && id.unsupported);
	if(unsupportedIdentifications.length===0)
		return;
	
	state.unsupported = true;
	state.id = unsupportedIdentifications.multiSort([id => id.confidence, id => C.FAMILIES.indexOf(id.family)], [true, false])[0];
}

// Will come up with a list of ids to check based on the results of the p.identify call
exports.checkIdentification = function checkIdentification(state, {DexvertError, formats}, cb)
{
	state.ids = state.identify.filter(id => id.from==="dexvert" && !id.unsupported).multiSort([id => (id.extMatch ? 0 : 1), id => id.confidence, id => C.FAMILIES.indexOf(id.family)], [false, true, false]);
	if(state.verbose>=4)
		XU.log`Identifications: ${state.ids}`;

	// If no ids and not brute forcing, we are done
	if(!state.brute && !state.brutePrograms && state.ids.length===0)
	{
		setFallthroughID(state);
		return setImmediate(cb);
	}

	// If we have ids and are not always brute forcing, we are ready to go
	if(state.ids.length>0 && !state.alwaysBrute)
	{
		if(state.verbose>=1)
			XU.log`\n${state.brute ? "Trying" : "Matched"} ${state.ids.length} formats${state.brute ? "" : `:\n${printUtil.columnizeObjects(state.ids.slice().reverse())}`}`;

		return setImmediate(cb);
	}
	
	state.preBruteOutputDirPath = state.output.absolute;

	// If we are brute forcing formats
	if(state.brute)
	{
		const idBase = {brute : true, from : "dexvert", confidence : 100};
		state.ids = state.brute.flatMap(family => Object.entries(formats[family]).filter(([, f]) => !f.meta.unsupported && !f.meta.bruteUnsafe).map(([formatid, f]) => ({family, formatid, magic : f.meta.name, extensions : f.meta.ext, ...idBase})));
		if(state.ids.length===0)
			return setImmediate(() => cb(new DexvertError(state, "No formats found to brute force.")));
		
		return setImmediate(cb);
	}

	// If we are brute forcing programs
	if(state.brutePrograms)
	{
		const idBase = {brute : true, bruteProgram : true, from : "dexvert", confidence : 100, family : "other"};
		tiptoe(
			function findPrograms()
			{
				fileUtil.glob(path.join(__dirname, "program"), "**/*.js", {nodir : true}, this);
			},
			function createIDSFromPrograms(programPaths)
			{
				state.ids = programPaths.map(programPath =>
				{
					const prog = require(programPath);	// eslint-disable-line node/global-require
					if(prog.meta.bruteUnsafe || prog.meta.informational)
						return undefined;
					const progid = path.basename(programPath, ".js");
					return {...idBase, formatid : progid};
				}).filterEmpty();

				this();
			},
			cb
		);
	}
	else
	{
		XU.log`\n${XU.cf.fg.red(`${XU.c.blink}ALERT`)}Shouldn't be possible to see this!`;
	}
};

// This will actually perform the processing of the next id in line (popped off the end for performance reasons)
exports.processNext = function processNext(state, p, cb)
{
	if(state.unsupported || state.ids.length===0)
		return setImmediate(cb);

	state.id = state.ids.shift();

	if(state.id.brute)
	{
		const bruteOutputDirPath = path.join(state.preBruteOutputDirPath, state.id.family, state.id.formatid);
		fs.mkdirSync(bruteOutputDirPath, {recursive : true});
		dexUtil.setStateOutput(state, bruteOutputDirPath);

		if(state.keepGoing)
			delete state.processed;
		
		if(state.id.bruteProgram)
			p.formats[state.id.family][state.id.formatid] = { meta : {name : `Program: ${state.id.formatid}`}, steps : [() => ({program : state.id.formatid})]};
	}

	if(state.verbose>=1)
		XU.log`Attempting to process as format: ${state.id.family}/${state.id.formatid}`;
	
	p.format = p.formats[state.id.family][state.id.formatid];
	p.family = p.families[state.id.family];

	function cbHandler(err)
	{
		if(err)
		{
			XU.log`Encountered error attempting to process as format: ${state.id.family}/${state.id.formatid}`;
			console.log(state);
			console.error(err);
		}

		setImmediate(cb);
	}

	p.util.flow.serial([
		() => p.util.file.tmpCWDCreate,
		subState =>
		{
			const ext = p.format.meta.safeExt ? p.format.meta.safeExt(state) : (p.format.meta.ext ? (p.format.meta.ext.includes(subState.input.ext.toLowerCase()) ? subState.input.ext : (state.id.fileSizeMatchExt || p.format.meta.ext[0])) : (state.id.fileSizeMatchExt || subState.input.ext || ""));	// eslint-disable-line max-len
			return p.util.file.safeInput(p.format.meta.keepFilename ? state.input.name : "in", ext.toLowerCase(), !!p.format.meta.symlinkUnsafe);
		},
		() => p.util.file.safeOutput,
		() => (ss, sp, scb) => ["filesRequired", "filesOptional"].flatMap(t => ((p.format.meta[t] || (() => []))(ss, ss.input.otherFiles) || [])).unique().parallelForEach((v, vcb) => fs.symlink(path.join(ss.input.dirPath, v), path.join(ss.cwd, (p.format.meta.keepFilename ? path.basename(v, path.extname(v)) : "in") + path.extname(v).toLowerCase()), vcb), scb),	// eslint-disable-line max-len
		() => p.util.meta.input,
		...(p.format.preSteps || []),
		subState => (subState.processed ? p.util.flow.noop : p.util.flow.serial(p.family.steps)),		// For files we don't need to convert, meta.input calls format.inputMeta which can set processed to true if the file is verified as valid
		...(p.format.postSteps || []),
		() => p.util.file.tmpCWDCleanup])(state, p, cbHandler);
};

// Will call the p.family.updateProcessed method which will set processed to true if the processing was successful
// We can't put this directly into exports.steps above because state.id.family isn't set until this function is actually called
exports.updateProcessed = function updateProcessed(state, p, cb)
{
	if(state.unsupported || !state.id)
		return setImmediate(cb);

	p.family.updateProcessed(state, p, cb);
};

// Called at the end of each processNext batch
exports.cleanup = function cleanup(state, p, cb)
{
	if(state.unsupported)
		return setImmediate(cb);
	
	const isBrute = state.id && state.id.brute;
	
	if(!state.processed)
	{
		delete state.id;

		// If we are brute forcing and were not successful, we need to delete the directory we created
		if(isBrute)
		{
			fileUtil.unlink(state.output.absolute, cb);
			return;
		}
	}

	return setImmediate(cb);
};
