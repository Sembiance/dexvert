import {xu, fg} from "xu";
import {XLog} from "xlog";
import {identify} from "./identify.js";
import {formats} from "./format/formats.js";
import {FileSet} from "./FileSet.js";
import {Program, clearRuntime, RUNTIME} from "./Program.js";
import {DexState} from "./DexState.js";
import {DexFile} from "./DexFile.js";
import {fileUtil, runUtil} from "xutil";
import {Identification} from "./Identification.js";
import {path} from "std";

export async function dexvert(inputFile, outputDir, {asFormat, asId, skipVerify, forbidProgram=[], programFlag={}, xlog=new XLog()}={})
{
	clearRuntime();
	for(const [programid, flags] of Object.entries(programFlag))
	{
		if(!Object.hasOwn(RUNTIME.globalFlags, programid))
			RUNTIME.globalFlags[programid] = {};
		Object.assign(RUNTIME.globalFlags[programid], flags);
	}

	for(const progid of forbidProgram)
		RUNTIME.forbidProgram.add(progid);

	if(!(await fileUtil.exists("/mnt/ram/dexvert/dexserver.pid")))
		throw new Error("dexserver not running!");
	if(inputFile.isDirectory)
		throw new Error(`Invalid input file, expected a file, got a directory: ${inputFile.absolute}`);
	if(!inputFile.isFile && !inputFile.isSymlink)
		throw new Error(`Invalid input file, expected a file. ${inputFile.absolute}`);
	if(!outputDir.isDirectory)
		throw new Error(`Invalid output directory, expected a directory. ${outputDir.absolute}`);
	
	const startedAt = performance.now();

	await runUtil.run("prlimit", ["--pid", Deno.pid, `--core=0`]);

	const ids = [];
	if(asFormat)
	{
		const [asFamilyid, asFormatid] = asFormat.split("/");
		if(!formats[asFormatid])
			throw new Error(`Invalid asFormat option specified, no such format: ${asFormatid}`);
		const asFormatFormat = formats[asFormatid];
		const asFormatId = {from : "dexvert", family : asFamilyid, formatid : asFormatid, magic : asFormatFormat.name, matchType : "magic", confidence : 100};
		for(const k of ["ext", "unsupported"])
		{
			if(asFormatFormat[k])
				asFormatId[k==="ext" ? "extensions" : k] = asFormatFormat[k];
		}

		// Since we are manually creating our Identification, we will need to manually call auxFiles
		if(asFormatFormat.auxFiles)
		{
			const otherFiles = (await Promise.all((await fileUtil.tree(inputFile.root, {depth : 1, nodir : true})).map(v => DexFile.create(v)))).filter(file => file.absolute!==inputFile.absolute);
			const otherDirs = await Promise.all((await fileUtil.tree(inputFile.root, {depth : 1, nofile : true})).map(v => DexFile.create(v)));
			const auxFiles = await asFormatFormat.auxFiles(inputFile, otherFiles, otherDirs);
			if(auxFiles)
				asFormatId.auxFiles = auxFiles;
		}

		ids.push(Identification.create(asFormatId));
		xlog.warn`Processing ${inputFile.pretty()} explicitly as format:\n\t${ids[0].pretty()}`;
	}
	else if(asId)
	{
		ids.push(asId);
		xlog.warn`Processing ${inputFile.pretty()} explicitly with identification:\n\t${asId.pretty()}`;
	}
	else
	{
		xlog.info`Getting identifications for ${inputFile.pretty()}`;
		ids.push(...(await identify(inputFile, {xlog : xlog.clone("error")})));
	}

	if(ids.some(id => id.from==="dexvert"))
		xlog.info`Identifications:\n\t${ids.map(id => id.pretty()).join("\n\t")}`;

	const dexState = DexState.create({original : {input : inputFile, output : outputDir}, ids, xlog});
	for(const id of ids)
	{
		if(id.from!=="dexvert" || id.unsupported)
			continue;

		const format = formats[id.formatid];
		xlog.info`\nAttempting to process identification: ${id.pretty()}`;

		// create a temporary ram cwd where all programs will run at (by default)
		const cwd = await fileUtil.genTempPath(undefined, `${id.family}_${id.formatid}`);
		await Deno.mkdir(cwd, {recursive : true});

		// create a temporary fileSet with the original input file and aux files so we can rsync to our cwd
		const originalInputFileSet = await FileSet.create(inputFile.root, "input", inputFile);
		if(id.auxFiles)
			await originalInputFileSet.addAll("aux", id.auxFiles);

		// copy over our files to cwd, this avoids issues with symlinks/file locks/programs modifying original source (though this latter case is only covered once, so don't do that heh)
		// NOTE! This rsync may produce FEWER files than we asked it to copy over. This can happy with the 'auxFiles' as an external process may have deleted an otherFile/otherDir
		const f = await originalInputFileSet.rsyncTo(cwd);

		// create a simple 'out' dir (or a unique name if taken already) and output our files there, this avoids issues where various programs choke on output paths that contain odd characters
		const outDirPath = (await fileUtil.exists(path.join(cwd, "out")) ? (await fileUtil.genTempPath(cwd, "out")) : path.join(cwd, "out"));
		await Deno.mkdir(outDirPath, {recursive : true});
		await f.add("outDir", outDirPath);

		// create a 'home' dir (or a unique name if taken already) and run programs with a HOME env set to that, this avoids issues when running the same program multiple times at once and it uses some sort of HOME .config lock file
		const homeFilePath = (await fileUtil.exists(path.join(cwd, "home")) ? (await fileUtil.genTempPath(cwd, "home")) : path.join(cwd, "home"));
		await Deno.mkdir(homeFilePath, {recursive : true});
		
		// create the files needed for java v17 to work (needed for program acx (AppleCommander) to work)
		await Deno.mkdir(path.join(homeFilePath, ".gentoo", "java-config-2"), {recursive : true});
		await Deno.symlink("/usr/lib/jvm/openjdk-bin-17", path.join(homeFilePath, ".gentoo", "java-config-2", "current-user-vm"));

		await f.add("homeDir", homeFilePath);

		dexState.startPhase({format, id, f});

		// rename the primary file to an easy filename that any program can handle: in<ext>
		if(!format.keepFilename)
		{
			const cwdFilename = "in";

			let cwdExt = null;

			if(format.safeExt)
			{
				cwdExt = typeof format.safeExt==="function" ? await format.safeExt(dexState) : format.safeExt;
				xlog.debug`format has safeext function and returned ${cwdExt}`;
			}
			
			if(cwdExt===null)
			{
				if(format.ext)	// eslint-disable-line unicorn/prefer-ternary
					cwdExt = format.ext.find(ext => ext===inputFile.ext.toLowerCase() || ext===id.fileSizeMatchExt) || format.ext[0];
				else
					cwdExt = inputFile.ext;
			}
			
			await f.input.rename(cwdFilename + cwdExt);

			// by default we rename the aux files to match, unless keepFilename is set to true
			if(f.aux)
			{
				for(const auxFile of f.files.aux)
				{
					const newAuxFilename = `${cwdFilename}${auxFile.ext.toLowerCase()}`;
					if(!(await fileUtil.exists(path.join(auxFile.dir, newAuxFilename))))
						await auxFile.rename(newAuxFilename);
				}
			}
		}

		const cleanup = async () =>
		{
			if(xlog.atLeast("trace"))
			{
				xlog.debug`${fg.red("NOT")} deleting cwd ${cwd}`;
			}
			else
			{
				xlog.debug`Deleting cwd ${cwd}...`;
				await fileUtil.unlink(cwd, {recursive : true});
			}
		};

		try
		{
			Object.assign(dexState.meta, await format.getMeta(f.input, dexState));
			
			// if we are untouched, mark ourself as processed and cleanup
			if(format.untouched===true || (typeof format.untouched==="function" && await format.untouched(dexState)))
			{
				// check family verification if our match type isn't a magic one or if we explicitly set verifyFamily (unless verifyFamily explicity set to false)
				const verifyUntouched = Object.hasOwn(format, "verifyUntouched") ? (typeof format.verifyUntouched==="function" ? await format.verifyUntouched(dexState) : !!format.verifyUntouched) : dexState.phase.id.matchType!=="magic";

				let isValid = true;
				if(verifyUntouched)
				{
					const extraValidatorData = format.family.verify ? (await dexState.format.family.verify(dexState, inputFile)) : {};
					if(extraValidatorData===false)
						isValid = false;
					
					if(extraValidatorData && format.verify && !(await format.verify({dexState, inputFile, ...extraValidatorData})))
						isValid = false;
				}
				
				if(isValid)
				{
					dexState.untouched = true;
					dexState.processed = true;
					await cleanup();
					break;
				}
			}

			// run any pre-converter pre format function
			if(format.pre)
				await format.pre(dexState);

			const tryProg = async function tryProg(prog, {isChain}={})
			{
				const progProps = Program.parseProgram(prog);
				if(RUNTIME.forbidProgram.has(progProps.programid))
					return xlog.info`Skipping converter ${prog} due to being in forbidProgram`, false;

				if(progProps.flags?.matchType && progProps.flags.matchType!==dexState.phase.id.matchType)
					return xlog.info`Skipping converter ${prog} due to matchType ${dexState.phase.id.matchType} not matching required ${progProps.flags.matchType}`, false;
				
				xlog.debug`Running converter ${prog}...`;

				const flags = {};

				// check to see if we are a packed format and we should set the program renameKeepFilename flag
				if(format.packed)
				{
					if(!(format.ext || []).includes(inputFile.ext.toLowerCase()))
						flags.renameKeepFilename = true;
					else
						flags.renameOut = true;
				}

				const r = await Program.runProgram(prog, dexState.f, {originalInput : dexState.original.input, isChain, format, xlog, flags});
				dexState.ran.push(r);

				// if our program explicitly states we are now processed, mark our dexState as such
				if(r.processed)
					dexState.processed = true;

				if(!skipVerify)
					xlog.info`Verifying ${(dexState.f.files.new || []).length.toLocaleString()} new files...`;

				// verify output files
				const newlyProducedFiles = [];
				await (dexState.f.files.new || []).parallelMap(async (newFile, newFileNum) =>
				{
					if(!skipVerify)
					{
						xlog.debug`Verifying file #${newFileNum.toLocaleString()} of ${dexState.f.files.new.length.toLocaleString()}: ${newFile.base}`;

						const failValidation = async msg =>
						{
							xlog.warn`${newFile.pretty()} FAILED validation ${msg}`;
							if(!xlog.atLeast("trace"))
								await fileUtil.unlink(newFile.absolute);

							return false;
						};

						// first, check family level validators
						const extraValidatorData = dexState.format.family.verify ? (await dexState.format.family.verify(dexState, newFile)) : {};
						if(extraValidatorData===false)
							return failValidation(`family ${dexState.format.family.pretty()}`);

						// if still valid, check format level validator
						if(format.verify && !(await format.verify({dexState, newFile, ...extraValidatorData})))
							return failValidation(`format ${format.pretty()}`);
					}

					// if a produced file is older than 2020, then we assume it's the proper date
					if((new Date(newFile.ts)).getFullYear()>=2020 && inputFile.ts<newFile.ts)
						await newFile.setTS(inputFile.ts);	// otherwise ensure the newly produce file has a timestamp equal to the input file

					newlyProducedFiles.push(newFile);
				});

				if(newlyProducedFiles.length)
				{
					xlog.info`Finished verifying files, yielded ${newlyProducedFiles.length.toLocaleString()} new files. Adding as output...`;
					await dexState.f.addAll("output", newlyProducedFiles);
				}

				dexState.f.removeType("new");

				return !!newlyProducedFiles.length;
			};

			const converters = format.converters ? (Array.isArray(format.converters) ? format.converters : await format.converters(dexState)) : [];

			const checkIfProcessed = async function checkIfProcessed(phaseConverter)
			{
				if((dexState.f.files.output?.length || 0)>0 || (format.processed && await format.processed(dexState)))
					dexState.processed = true;
				
				if(dexState.processed && phaseConverter)
					dexState.phase.converter = phaseConverter;

				return dexState.processed;
			};

			if(converters.some(v => Array.isArray(v)))
			{
				// The 'new' approach (see archive/iso.js), an array of arrays
				// In order, each array should be performaned (regardless of outcome of previous array). For each array, try each program in order, stopping if any produce new files
				xlog.info`\nTrying ${fg.yellowDim(converters.length)} batches of ${format.formatid} converters...`;

				const phaseConverters = [];
				for(const [i, batchRaw] of Object.entries(converters))
				{
					const batch = typeof batchRaw==="function" ? batchRaw(dexState) : batchRaw;
					xlog.info`\nTrying ${fg.yellowDim(batch.length)} converters in batch ${i}...`;

					for(const converter of batch)
					{
						if(!await tryProg(converter))
							continue;
						
						phaseConverters.push(converter);
						break;
					}
				}

				if(phaseConverters.length)
					await checkIfProcessed(phaseConverters.join(" & "));
			}
			else
			{
				// The 'classic' approach and array of strings (or a function that returns a string)
				// Each string is a program to run. Sometimes that string is two programs to both run like prog1 & prog2
				xlog.info`\nTrying ${fg.yellowDim(converters.length)} ${format.formatid} converters...`;

				for(const converterRaw of (converters || []))
				{
					const converter = typeof converterRaw==="function" ? converterRaw(dexState) : converterRaw;
					if(!converter)
						continue;
						
					const progs = converter.split("&").map(v => v.trim());
					for(const [i, prog] of Object.entries(progs))
						await tryProg(prog, {isChain : i>0});

					if(await checkIfProcessed(converter))
						break;
				}
			}

			// run any post-converter post format function
			if(format.post)
				await format.post(dexState);
		}
		catch(err)
		{
			dexState.phase.err = err;
			xlog.error`${fg.red(`${xu.c.blink}dexvert failed`)} for file ${inputFile.absolute} with error: ${xu.inspect(err)}`;
		}

		// if we are processed, rsync any "output" files back to our original output directory, making sure we don't include the "out" tmp dir we made
		// important to do this before cleanup() since that will delete all tmp dirs including output files
		if(dexState.processed)
		{
			xlog.debug`Rsyncing output files back to target output directory...`;
			await runUtil.run("rsync", ["-a", "--prune-empty-dirs", `${dexState.f.outDir.absolute}/`, `${outputDir.absolute}/`]);

			xlog.debug`Creating FileSet for output files...`;
			dexState.created = await FileSet.create(outputDir.absolute, "output", await fileUtil.tree(outputDir.absolute, {nodir : true}));
			// We used to rsync each file individually this way, but this was ungodly slow on large archives like SpanishScene.iso
			// So now we just rsync our output directory... should be safe :)
			//dexState.created = await dexState.f.rsyncTo(outputDir.absolute, {type : "output", relativeFrom : outDirPath});
		}

		await cleanup();

		if(dexState.processed)
			break;
	}

	dexState.duration = (performance.now()-startedAt);
	return dexState;
}
