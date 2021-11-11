import {xu, fg} from "xu";
import {identify} from "./identify.js";
import {Format} from "./Format.js";
import {FileSet} from "./FileSet.js";
import {Converter} from "./Converter.js";
import {DexState} from "./DexState.js";
import {fileUtil, runUtil} from "xutil";
import {Identification} from "./Identification.js";
import * as path from "https://deno.land/std@0.111.0/path/mod.ts";

const DEFAULT_QUOTA_DISK = xu.GB*10;

export async function dexvert(inputFile, outputDir, {verbose, asFormat})
{
	if(!inputFile.isFile)
		throw new Error(`Invalid input file, expected file. ${inputFile.absolute}`);
	if(!outputDir.isDirectory)
		throw new Error(`Invalid output directory, expected directory. ${inputFile.absolute}`);

	const formats = await Format.loadFormats();

	const ids = [];
	if(asFormat)
	{
		const [asFamilyid, asFormatid] = asFormat.split("/");
		const asId = {from : "dexvert", family : asFamilyid, formatid : asFormatid, magic : formats[asFormatid].name, matchType : "magic", confidence : 100};
		for(const k of ["ext", "unsupported"])
		{
			if(formats[asFormatid][k])
				asId[k] = formats[asFormatid][k];
		}
		ids.push(Identification.create(asId));
	}
	else
	{
		ids.push(...(await identify(inputFile, {verbose})).filter(id => id.from==="dexvert" && !id.unsupported));
	}

	if(verbose>=2)
		xu.log`Identifications:\n\t${ids.map(id => id.pretty()).join("\n\t")}`;
	
	if(ids.length===0)
		return;

	//posix.setrlimit("core", {soft : 0});

	const dexState = DexState.create({original : {input : inputFile, output : outputDir}, verbose});
	for(const id of ids)
	{
		const format = formats[id.formatid];
		if(verbose>=1)
			xu.log`Attempting to process identification: ${id.pretty()}`;

		// create a temporary ram cwd where all programs will run at (by default)
		const cwd = await fileUtil.genTempPath(undefined, `${id.family}-${id.formatid}`);
		await Deno.mkdir(cwd, {recursive : true});

		// create a temporary fileSet with the original input file and aux files so we can rsync to our cwd
		const originalInputFileSet = await FileSet.create(inputFile.root, "input", inputFile);
		if(id.auxFiles)
			originalInputFileSet.addAll("aux", id.auxFiles);

		// copy over our files to cwd, this avoids issues with symlinks/file locks/programs modifying original source (though this latter case is only covered once, so don't do that heh)
		// TODO Need to test with a directory from auxfiles, like font/amigaBitmapFont
		const f = await originalInputFileSet.rsyncTo(cwd);

		// create a simple 'out' dir (or a unique name if taken already) and output our files there, this avoids issues where various programs choke on output paths that contain odd characters
		const outDirPath = (await fileUtil.exists(path.join(cwd, "out")) ? (await fileUtil.genTempPath(cwd, "out")) : path.join(cwd, "out"));
		await Deno.mkdir(outDirPath, {recursive : true});
		await f.add("outDir", outDirPath);

		// create a 'home' dir (or a unique name if taken already) and run programs with a HOME env set to that, this avoids issues when running the same program multiple times at once and it uses some sort of HOME .config lock file
		const homeFilePath = (await fileUtil.exists(path.join(cwd, "home")) ? (await fileUtil.genTempPath(cwd, "home")) : path.join(cwd, "home"));
		await Deno.mkdir(homeFilePath, {recursive : true});
		await f.add("homeDir", homeFilePath);

		dexState.startPhase({format, id, f});

		// rename the primary file to an easy filename that any program can handle: in<ext>
		const cwdFilename = format.keepFilename ? inputFile.name : "in";

		let cwdExt = null;
		if(format.safeExt)
			cwdExt = await format.safeExt(dexState);
		else if(format.ext)
			cwdExt = format.ext.find(ext => ext===inputFile.ext.toLowerCase()) || format.ext[0];
		else
			cwdExt = inputFile.ext;
		
		await f.input.rename(cwdFilename + cwdExt);

		// restrict the size of our out dir by mounting a RAM disk of a static size to it, that way we can't fill up our entire hard drive with misbehaving programs
		if(verbose>=5)
			xu.log`${fg.red("NOT")} mounting ${cwd}/out as a RAM disk, due to verbose>=5`;
		else
			await runUtil.run("sudo", ["mount", "-t", "tmpfs", "-o", `size=${DEFAULT_QUOTA_DISK},mode=0777,nodev,noatime`, "tmpfs", f.outDir.absolute]);

		const cleanup = async () =>
		{
			if(verbose>=5)
			{
				xu.log`${fg.red("NOT")} deleting cwd ${cwd} due to verbose>=5`;
			}
			else
			{
				await runUtil.run("sudo", ["umount", f.outDir.absolute]);
				await Deno.remove(cwd, {recursive : true});
			}
		};

		try
		{
			Object.assign(dexState.meta, await format.getMeta(f.input, format));
			
			if(format.untouched===true || (typeof format.untouched==="function" && await format.untouched(dexState)))
			{
				dexState.processed = true;
				await cleanup();
				break;
			}

			if(format.pre)
				await format.pre(dexState);
			
			for(const converter of (format.converters || []).map(v => Converter.create(dexState, v)))
			{
				await converter.run();

				// TODO
			}

			if(format.post)
				await format.post(dexState);

			/*
			subState => (subState.processed ? p.util.flow.noop : p.util.flow.serial(p.family.steps)),		// For files we don't need to convert, meta.input calls format.inputMeta which can set processed to true if the file is verified as valid
			() => p.util.file.tmpCWDCleanup])(state, p, cbHandler);
				
			(state, p) => p.util.file.findValidOutputFiles(true),
			() => exports.updateProcessed,
			() => exports.cleanup
			
			checkShouldContinue)
				*/
		}
		catch(err)
		{
			xu.log`dexvert failed with error: ${err}`;
		}

		await cleanup();
	}

	return dexState;
}

/*

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

*/
