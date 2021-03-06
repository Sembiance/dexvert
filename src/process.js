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

		if(!state.unsupported && !state.asFormat)
			setFallthroughID(state);

		return false;
	}

	return true;
}

// List of steps to perform for processing
exports.steps =
[
	(state, p) => p.util.file.glob(state.output.absolute, "**", {nodir : true}, existingOutputFiles => existingOutputFiles.length===0, `Output directory ${state.output.absolute} is not empty`),
	(state, p) => (state.asFormat ? p.util.flow.noop : p.util.flow.serial(p.identify.steps)),
	() => exports.checkIdentification,
	(state0, p0) => p0.util.flow.batchRepeatUntil([
		() => exports.processNext,
		(state, p) => p.util.file.findValidOutputFiles(true),
		() => exports.updateProcessed,
		() => exports.cleanup], checkShouldContinue)
];

// Called if we were not able to process it as anything, then we still want to set state.id to our "best guess", usually an unsupported file format
function setFallthroughID(state)
{
	delete state.id;

	// If we have any unsupported dexvert matches that were magic matches, include them here
	const unsupportedIdentifications = state.identify.filter(id => id.from==="dexvert" && id.unsupported && id.matchType==="magic");
	if(unsupportedIdentifications.length>=1)
	{
		state.unsupported = true;
		state.id = unsupportedIdentifications.multiSort([id => id.matchType==="ext", id => id.confidence, id => C.FAMILIES.indexOf(id.family)], [true, true, false])[0];
	}
}

// Will come up with a list of ids to check based on the results of the p.identify call
exports.checkIdentification = function checkIdentification(state, {DexvertError, formats}, cb)
{
	if(state.asFormat)
	{
		const [asFamily, asFormatid] = state.asFormat.split("/");
		const formatMeta = formats[asFamily][asFormatid].meta;
		const asMatch = {from : "dexvert", family : asFamily, formatid : asFormatid, magic : formatMeta.name, matchType : "magic", confidence : 100, originalConfidence : 100};
		if(formatMeta.ext)
			asMatch.extensions = formatMeta.ext;
		["encoding", "confidenceAdjust", "website", "unsupported", "mimeType", "hljsLang", "fallback"].forEach(k =>
		{
			if(formatMeta[k])
				asMatch[k] = formatMeta[k];
		});

		["trustMagic", "unsupported", "untouched", "highConfidence"].forEach(key =>
		{
			if(formatMeta[key])
				asMatch[key] = true;
		});

		// NOTE: Some id flags are not correctly emulated here, such as extMatch/filenameMatch, etc. This might cause problems when processing a format that checks these for whatever reason

		state.ids = [asMatch];
	}
	else
	{
		state.ids = state.identify.filter(id => id.from==="dexvert" && !id.unsupported);
	}

	if(state.verbose>=4)
		XU.log`Identifications: ${state.ids}`;

	// If no ids and not brute forcing, we are done
	if(!state.brute && !state.brutePrograms && state.ids.length===0)
	{
		if(!state.asFormat)
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

	// If we are brute forcing programs
	if(state.brutePrograms)
	{
		const idBase = {brute : true, bruteProgram : true, from : "dexvert", confidence : 100, family : "other"};
		tiptoe(
			function findPrograms()
			{
				let programsParentPath = path.join(__dirname, "program");
				if(state.brute)
					programsParentPath = path.join(programsParentPath, state.brute[0]);
				fileUtil.glob(programsParentPath, "**/*.js", {nodir : true}, this);
			},
			function createIDSFromPrograms(programPaths)
			{
				state.ids = programPaths.map(programPath =>
				{
					const prog = require(programPath);	// eslint-disable-line node/global-require
					if(prog.meta.unsafe || prog.meta.informational)
						return undefined;
					const progid = path.basename(programPath, ".js");
					return {...idBase, formatid : progid};
				}).filterEmpty();

				this();
			},
			cb
		);
	}
	else if(state.brute)
	{
		const idBase = {brute : true, from : "dexvert", confidence : 100};
		state.ids = state.brute.flatMap(family => Object.entries(formats[family]).filter(([, f]) => !f.meta.unsupported && !f.meta.unsafe).map(([formatid, f]) => ({family, formatid, magic : f.meta.name, extensions : f.meta.ext, ...idBase})));
		if(state.ids.length===0)
			return setImmediate(() => cb(new DexvertError(state, "No formats found to brute force.")));
		
		return setImmediate(cb);
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
		return p.util.meta.input(state, p, cb);

	state.id = state.ids.shift();
	
	delete state.extraFilenames;

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
			console.error(`Encountered error attempting to process ${state.input.absolute} as format: ${state.id.family}/${state.id.formatid}`);
			if(state.verbose>=1)
				console.log(state);
			console.error(err);
		}

		setImmediate(cb);
	}

	p.util.flow.serial([
		() => p.util.file.tmpCWDCreate,
		subState =>
		{
			let ext=null;
			if(p.format.meta.safeExt)
				ext = p.format.meta.safeExt(state);
			else if(p.format.meta.ext)
				ext = (p.format.meta.ext.includes(subState.input.ext.toLowerCase()) ? subState.input.ext : (state.id.fileSizeMatchExt || p.format.meta.ext[0]));
			else
				ext = (state.id.fileSizeMatchExt || subState.input.ext || "");

			return p.util.file.safeInput([true, "input"].includes(p.format.meta.keepFilename) ? state.input.name : "in", ext.toLowerCase(), [true, "input"].includes(p.format.meta.symlinkUnsafe));
		},
		() => p.util.file.safeOutput,
		() => (ss, sp, scb) => ["filesRequired", "filesOptional"].flatMap(t => ((p.format.meta[t] || (() => []))(ss, ss.input.otherFiles, ss.input.otherDirs) || [])).unique().parallelForEach((v, vcb) =>
		{
			if(!ss.extraFilenames)
				ss.extraFilenames = [];
			const extraFilename = ([true, "extras"].includes(p.format.meta.keepFilename) ? path.basename(v, path.extname(v)) : "in") + path.extname(v).toLowerCase();
			ss.extraFilenames.push(extraFilename);

			const extraDestFilePath = path.join(ss.cwd, extraFilename);
			const extraSrcFilePath = path.join(ss.input.dirPath, v);
			if([true, "extras"].includes(p.format.meta.symlinkUnsafe))
			{
				if(fs.statSync(extraSrcFilePath).isDirectory())
					fileUtil.copyDir(extraSrcFilePath, extraDestFilePath, vcb);
				else
					fs.copyFile(extraSrcFilePath, extraDestFilePath, vcb);
			}
			else
			{
				fs.symlink(extraSrcFilePath, extraDestFilePath, vcb);
			}
		}, scb),
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
	
	const isBrute = state.id?.brute;
	
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
