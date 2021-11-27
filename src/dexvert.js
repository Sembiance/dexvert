import {xu, fg} from "xu";
import {identify} from "./identify.js";
import {formats} from "./format/formats.js";
import {FileSet} from "./FileSet.js";
import {Program} from "./Program.js";
import {DexState} from "./DexState.js";
import {fileUtil, runUtil} from "xutil";
import {Identification} from "./Identification.js";
import {path} from "std";

export async function dexvert(inputFile, outputDir, {asFormat}={})
{
	if(!(await fileUtil.exists("/mnt/ram/dexvert/dexserver.pid")))
		throw new Error("dexserver not running!");
	if(!inputFile.isFile)
		throw new Error(`Invalid input file, expected file. ${inputFile.absolute}`);
	if(!outputDir.isDirectory)
		throw new Error(`Invalid output directory, expected directory. ${inputFile.absolute}`);

	await runUtil.run("prlimit", ["--pid", Deno.pid, `--core=0`]);

	const ids = [];
	if(asFormat)
	{
		const [asFamilyid, asFormatid] = asFormat.split("/");
		if(!formats[asFormatid])
			throw new Error(`Invalid asFormat option specified, no such format: ${asFormatid}`);
		const asId = {from : "dexvert", family : asFamilyid, formatid : asFormatid, magic : formats[asFormatid].name, matchType : "magic", confidence : 100};
		for(const k of ["ext", "unsupported"])
		{
			if(formats[asFormatid][k])
				asId[k==="ext" ? "extensions" : k] = formats[asFormatid][k];
		}
		ids.push(Identification.create(asId));
		xu.log1`Processing ${inputFile.pretty()} explicitly as format: ${ids[0].pretty()}`;
	}
	else
	{
		xu.log1`Getting identifications for ${inputFile.pretty()}`;
		ids.push(...(await identify(inputFile, {quiet : true})).filter(id => id.from==="dexvert" && !id.unsupported));
	}

	if(ids.length===0)
		return;

	xu.log2`Identifications:\n\t${ids.map(id => id.pretty()).join("\n\t")}`;

	const dexState = DexState.create({original : {input : inputFile, output : outputDir}});
	for(const id of ids)
	{
		const format = formats[id.formatid];
		xu.log2`\nAttempting to process identification: ${id.pretty()}`;

		// create a temporary ram cwd where all programs will run at (by default)
		const cwd = await fileUtil.genTempPath(undefined, `${id.family}-${id.formatid}`);
		await Deno.mkdir(cwd, {recursive : true});

		// create a temporary fileSet with the original input file and aux files so we can rsync to our cwd
		const originalInputFileSet = await FileSet.create(inputFile.root, "input", inputFile);
		if(id.auxFiles)
			originalInputFileSet.addAll("aux", id.auxFiles);

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
				cwdExt = await format.safeExt(dexState);
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
			if(xu.verbose>=5)
				xu.log5`${fg.red("NOT")} deleting cwd ${cwd} due to verbose>=5`;
			else
				await fileUtil.unlink(cwd, {recursive : true});
		};

		try
		{
			Object.assign(dexState.meta, await format.getMeta(f.input));
			
			// if we are untouched, mark ourself as processed and cleanup
			if(format.untouched===true || (typeof format.untouched==="function" && await format.untouched(dexState)))
			{
				dexState.processed = true;
				await cleanup();
				break;
			}

			// run any pre-converter pre format function
			if(format.pre)
				await format.pre(dexState);
			
			const converters = Array.isArray(format.converters) ? format.converters : await format.converters(dexState);
			xu.log3`\nTrying ${fg.yellowDim(converters.length)} ${format.formatid} converters...`;

			// try each converter specificied, until we have output files or have been marked as processed
			for(const converter of (converters || []))
			{
				const progs = converter.split("&").map(v => v.trim());
				for(const [i, prog] of Object.entries(progs))
				{
					xu.log4`Running converter ${prog}...`;

					const r = await Program.runProgram(prog, dexState.f, {originalInput : dexState.original.input, isChain : i>0});
					dexState.ran.push(r);

					xu.log3`Verifying ${(dexState.f.files.new || []).length} new files...`;

					// verify output files
					for(const newFile of dexState.f.files.new || [])
					{
						const isValid = await dexState.format.family.verify(dexState, newFile, await identify(newFile, {quiet : true}));
						if(!isValid)
						{
							xu.log2`${fg.red("DELETING OUTPUT FILE")} ${newFile.pretty()} due to failing verification from ${dexState.format.family.pretty()} family`;
							if(xu.verbose>=5)
								xu.log5`NOT deleting it, due to verbose>=5`;
							else
								await fileUtil.unlink(newFile.absolute);
							continue;
						}

						// if a produced file is older than 2020, then we assume it's the proper date
						if((new Date(newFile.ts)).getFullYear()>=2020 && inputFile.ts<newFile.ts)
						{
							newFile.ts = inputFile.ts;
							await Deno.utime(newFile.absolute, Math.floor(inputFile.ts/xu.SECOND), Math.floor(inputFile.ts/xu.SECOND));
						}

						await dexState.f.add("output", newFile);
					}

					dexState.f.removeType("new");
				}

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
			console.error(`${fg.red(`${xu.c.blink}dexvert failed`)} with error: ${xu.inspect(err)}`);
		}

		// if we are processed, rsync any "output" files back to our original output directory, making sure we don't include the "out" tmp dir we made
		// important to do this before cleanup() since that will delete all tmp dirs including output files
		if(dexState.processed)
			dexState.created = await dexState.f.rsyncTo(outputDir.absolute, {type : "output", relativeFrom : outDirPath});

		await cleanup();

		if(dexState.processed)
			break;
	}

	return dexState;
}
