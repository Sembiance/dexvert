import {xu, fg} from "xu";
import {identify} from "./identify.js";
import {formats} from "./format/formats.js";
import {FileSet} from "./FileSet.js";
import {Program} from "./Program.js";
import {DexState} from "./DexState.js";
import {DexFile} from "./DexFile.js";
import {fileUtil, runUtil} from "xutil";
import {Identification} from "./Identification.js";
import {path} from "std";

export async function dexvert(inputFile, outputDir, {asFormat, xlog=xu.xLog()}={})
{
	if(!(await fileUtil.exists("/mnt/ram/dexvert/dexserver.pid")))
		throw new Error("dexserver not running!");
	if(!inputFile.isFile)
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
		const asId = {from : "dexvert", family : asFamilyid, formatid : asFormatid, magic : asFormatFormat.name, matchType : "magic", confidence : 100};
		for(const k of ["ext", "unsupported"])
		{
			if(asFormatFormat[k])
				asId[k==="ext" ? "extensions" : k] = asFormatFormat[k];
		}

		// Since we are manually creating our Identification, we will need to manually call auxFiles
		if(asFormatFormat.auxFiles)
		{
			const otherFiles = (await Promise.all((await fileUtil.tree(inputFile.root, {depth : 1, nodir : true})).map(v => DexFile.create(v)))).filter(file => file.absolute!==inputFile.absolute);
			const otherDirs = await Promise.all((await fileUtil.tree(inputFile.root, {depth : 1, nofile : true})).map(v => DexFile.create(v)));
			const auxFiles = await asFormatFormat.auxFiles(inputFile, otherFiles, otherDirs);
			if(auxFiles)
				asId.auxFiles = auxFiles;
		}

		ids.push(Identification.create(asId));
		xlog.warn`Processing ${inputFile.pretty()} explicitly as format:\n\t${ids[0].pretty()}`;
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
		if(!format.keepFilename)
		{
			const cwdFilename = "in";

			let cwdExt = null;
			if(format.safeExt)
				cwdExt = typeof format.safeExt==="function" ? await format.safeExt(dexState) : format.safeExt;
			else if(format.ext)
				cwdExt = format.ext.find(ext => ext===inputFile.ext.toLowerCase()) || format.ext[0];
			else
				cwdExt = inputFile.ext;
			
			await f.input.rename(cwdFilename + cwdExt);

			// by default we rename the aux files to match, unless keepFilename is set to true
			if(f.aux)
			{
				for(const auxFile of f.files.aux)
					await auxFile.rename(`${cwdFilename}${auxFile.ext.toLowerCase()}`);
			}
		}

		const cleanup = async () =>
		{
			if(xlog.atLeast("trace"))
				xlog.debug`${fg.red("NOT")} deleting cwd ${cwd}`;
			else
				await fileUtil.unlink(cwd, {recursive : true});
		};

		try
		{
			Object.assign(dexState.meta, await format.getMeta(f.input, dexState));
			
			// if we are untouched, mark ourself as processed and cleanup
			if(format.untouched===true || (typeof format.untouched==="function" && await format.untouched(dexState)))
			{
				dexState.untouched = true;
				dexState.processed = true;
				await cleanup();
				break;
			}

			// run any pre-converter pre format function
			if(format.pre)
				await format.pre(dexState);
			
			const converters = format.converters ? (Array.isArray(format.converters) ? format.converters : await format.converters(dexState)) : [];
			xlog.info`\nTrying ${fg.yellowDim(converters.length)} ${format.formatid} converters...`;

			// try each converter specificied, until we have output files or have been marked as processed
			for(const converter of (converters || []))
			{
				const progs = converter.split("&").map(v => v.trim());
				for(const [i, prog] of Object.entries(progs))
				{
					xlog.debug`Running converter ${prog}...`;

					const r = await Program.runProgram(prog, dexState.f, {originalInput : dexState.original.input, isChain : i>0, format, xlog});
					dexState.ran.push(r);

					xlog.info`Verifying ${(dexState.f.files.new || []).length} new files...`;

					// verify output files
					await (dexState.f.files.new || []).parallelMap(async newFile =>
					{
						let isValid = true;
						
						// first, check family level validators
						const extraValidatorData = dexState.format.family.verify ? (await dexState.format.family.verify(dexState, newFile)) : {};
						if(extraValidatorData===false)
						{
							xlog.warn`${newFile.pretty()} FAILED validation from family ${dexState.format.family.pretty()}`;
							isValid = false;
						}
						
						// if still valid, check format level validator
						if(isValid && format.verify && !(await format.verify({dexState, newFile, ...extraValidatorData})))
						{
							xlog.warn`${newFile.pretty()} FAILED validation from format ${format.pretty()}`;
							isValid = false;
						}

						if(!isValid)
						{
							if(!xlog.atLeast("trace"))
								await fileUtil.unlink(newFile.absolute);
							return;
						}

						// if a produced file is older than 2020, then we assume it's the proper date
						if((new Date(newFile.ts)).getFullYear()>=2020 && inputFile.ts<newFile.ts)
							await newFile.setTS(inputFile.ts);	// otherwise ensure the newly produce file has a timestamp equal to the input file

						await dexState.f.add("output", newFile);
					});

					dexState.f.removeType("new");
				}

				xlog.info`Finished verifying files, yielded ${(dexState.f.files.output?.length || 0)} output files.`;
				if((dexState.f.files.output?.length || 0)>0)
					dexState.processed = true;

				if(dexState.processed)
				{
					dexState.phase.converter = converter;
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
			xlog.error`${fg.red(`${xu.c.blink}dexvert failed`)} with error: ${xu.inspect(err)}`;
		}

		// if we are processed, rsync any "output" files back to our original output directory, making sure we don't include the "out" tmp dir we made
		// important to do this before cleanup() since that will delete all tmp dirs including output files
		if(dexState.processed)
		{
			await runUtil.run("rsync", ["-a", `${dexState.f.outDir.absolute}/`, `${outputDir.absolute}/`]);
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
