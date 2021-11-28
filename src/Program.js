import {xu, fg} from "xu";
import {fileUtil, runUtil} from "xutil";
import {path} from "std";
import {validateClass, validateObject} from "./validate.js";
import {RunState} from "./RunState.js";
import {FileSet} from "./FileSet.js";
import {DexFile} from "./DexFile.js";
import {run as runDOS} from "./dosUtil.js";
import {run as runQEMU, QEMUIDS} from "./qemuUtil.js";

const DEFAULT_TIMEOUT = xu.MINUTE*5;

export class Program
{
	programid = this.constructor.name;
	loc = "local";
	baseKeys = Object.keys(this);

	// builder to get around the fact that constructors can't be async
	static create()
	{
		const program = new this();

		if(Object.hasOwn(program, "bin") && Object.hasOwn(program, "exec"))
			throw new Error(`class [${this.constructor.name}] can't have both [bin] and [exec] properties.`);

		validateClass(program, {
			// required
			programid : {type : "string", required : true},	// automatically set to the constructor name
			loc       : {type : "string", required : true, enum : ["local", "dos", ...QEMUIDS]},

			// meta
			flags          : {type : Object},
			gentooPackage  : {types : ["string", Array]},
			gentooOverlay  : {type : "string"},
			gentooUseFlags : {type : "string"},
			notes          : {type : "string"},
			renameOut      : {types : [Object, "boolean"]},
			runOptions     : {types : [Object, "function"]},
			unsafe         : {type : "boolean"},
			website        : {type : "string", url : true},

			// execution
			args       : {type : "function", length : [0, 1]},
			bin        : {type : "string"},
			chain      : {types : ["function", "string"]},
			chainCheck : {type : "function", length : [0, 3]},
			cwd        : {type : "function", length : [0, 1]},
			diskQuota  : {type : "number", range : [1]},
			dosData    : {type : "function", length : [0, 1]},
			exec       : {type : "function", length : [0, 1]},
			outExt     : {types : ["function", "string"]},
			post       : {type : "function", length : [0, 1]},
			pre        : {type : "function", length : [0, 1]},
			qemuData   : {type : "function", length : [0, 1]},
			verify     : {type : "function", length : [0, 2]}
		});

		if(program.renameOut && Object.isObject(program.renameOut))
			validateObject(program.renameOut, {ext : {type : "string"}, name : {type : "boolean"}, regex : {type : RegExp}, renamer : {type : ["function"]}, multipleOnly : {type : "boolean"}});

		return program;
	}

	// runs the current program with the given input and output FileSets and various options
	async run(f, {timeout=DEFAULT_TIMEOUT, flags={}, originalInput, chain, suffix="", isChain}={})
	{
		if(!(f instanceof FileSet))
			throw new Error(`Program ${fg.orange(this.programid)} run didn't get a FileSet as arg 1`);
		
		const unknownFlags = Object.keys(flags).subtractAll(Object.keys(this.flags || {}));
		if(unknownFlags.length>0)
			throw new Error(`Program ${fg.orange(this.programid)} run got unknown flags: ${unknownFlags.join(" ")}`);
		
		// restrict the size of our out dir by mounting a RAM disk of a static size to it, that way we can't fill up our entire hard drive with misbehaving programs
		if(this.diskQuota)
			await runUtil.run("sudo", ["mount", "-t", "tmpfs", "-o", `size=${this.diskQuota},mode=0777,nodev,noatime`, "tmpfs", f.outDir.absolute]);

		// create a RunState to store program results/meta
		const r = RunState.create({programid : this.programid, f, flags});
		r.cwd = f.root;
		if(this.cwd)
		{
			const newCWD = await this.cwd(r);
			r.cwd = newCWD.startsWith("/") ? newCWD : path.resolve(f.root, newCWD);
		}

		if(this.pre)
			await this.pre(r);

		if(this.exec)
		{
			// run arbitrary javascript code
			xu.log3`Program ${fg.orange(this.programid)} executing ${".exec"} steps`;
			await this.exec(r);
		}
		else if(this.loc==="local")
		{
			// run a program on disk
			r.bin = this.bin;
			r.args = (this.args ? await this.args(r) : []).map(arg => arg.toString());
			r.runOptions = {cwd : r.cwd, timeout};
			if(f.homeDir)
				r.runOptions.env = {HOME : f.homeDir.absolute};
			if(xu.verbose>=4)
				r.runOptions.verbose = true;
			if(this.runOptions)
				Object.assign(r.runOptions, typeof this.runOptions==="function" ? await this.runOptions(r) : this.runOptions);
				
			xu.log3`Program ${fg.orange(this.programid)} running as \`${this.bin} ${r.args.map(arg => (arg.includes(" ") ? `"${arg}"` : arg)).join(" ")}\`${xu.verbose>=4 ? ` with options ${xu.inspect(r.runOptions).squeeze()}` : ""}`;
			const {stdout, stderr, status} = await runUtil.run(this.bin, r.args, r.runOptions);
			Object.assign(r, {stdout, stderr, status});
		}
		else if(this.loc==="dos")
		{
			r.dosData = {root : f.root, cmd : this.bin};
			r.dosData.args = this.args ? await this.args(r) : [];
			if(this.dosData)
				Object.assign(r.dosData, await this.dosData(r));

			r.status = await runDOS(r.dosData);
		}
		else if(QEMUIDS.includes(this.loc))
		{
			r.qemuData = {f, cmd : this.bin, osid : this.loc};
			r.qemuData.args = this.args ? await this.args(r) : [];
			if(this.qemuData)
				Object.assign(r.qemuData, await this.qemuData(r));

			r.status = await runQEMU(r.qemuData);
		}

		if(f.outDir)
		{
			// we may have new files on disk in f.outDir

			// first we have to run fixPerms in order to ensure we can access the new files
			await runUtil.run(Program.binPath("fixPerms"), [], {cwd : f.outDir.absolute});

			// delete empty files/broken symlinks. find is very fast at this, so use that
			await runUtil.run("find", [f.outDir.absolute, "-type", "f", "-empty", "-delete"]);
			await runUtil.run("find", [f.outDir.absolute, "-xtype", "l", "-delete"]);

			// also delete any 'special' files that may be dangerous to process. block special, character special named pipe, socket
			await runUtil.run("find", [f.outDir.absolute, "-type", "b,c,p,s", "-delete"]);

			// now find any new files on disk in the output dir that we don't yet
			for(const newFilePath of (await fileUtil.tree(f.outDir.absolute, {nodir : true})).subtractAll([...(f.files.output || []), ...(f.files.prev || []), ...(f.files.new || [])].map(v => v.absolute)))
			{
				// if the new file is identical to our input file, delete it
				if(await fileUtil.areEqual(newFilePath, f.input.absolute))
				{
					xu.log2`Program ${fg.orange(this.programid)} deleting output file ${newFilePath} due to being identical to input file ${f.input.pretty()}`;
					await fileUtil.unlink(newFilePath);
					continue;
				}

				const newFile = await DexFile.create({root : f.root, absolute : newFilePath});

				// if this program has a custom verification step, check that
				if(this.verify && !(await this.verify(r, newFile)))
				{
					xu.log2`Program ${fg.orange(this.programid)} deleting output file ${newFilePath} due to failing program.verify() function`;
					await fileUtil.unlink(newFilePath);
					continue;
				}

				// add our new file to our fileset
				await f.add("new", newFile);
			}
		}

		// sort the filenames by depth and then by filename
		if(f.files.new)
			f.files.new.sortMulti([file => file.rel.split("/").length, file => file.base]);

		if(this.post)
		{
			try { await this.post(r); }
			catch(err) { xu.log`Program post ${fg.orange(this.programid)} threw error ${err}`; }
		}

		// if we have some new files, time to rename them
		if(f.outDir && f.files.new?.length && this.renameOut!==false)
		{
			const ro = Object.assign({ext : typeof this.outExt==="function" ? this.outExt(r) || "" : this.outExt || "", name : true}, this.renameOut);
			const newName = (ro.name===true ? (originalInput?.name || f.input.name) : (ro.name || f.new.name));
			const restreamerOpts = {newName, suffix, numFiles : f.files.new.length};

			// See if we have more advanced renaming
			if(ro.regex && (f.files.new.length>1 || !ro.multipleOnly))
			{
				let renamer = null;
				let renamerNum = null;
				for(const [i, testRenamer] of Object.entries(ro.renamer))
				{
					const filenames = f.files.new.map(newFile =>
					{
						try
						{
							const parts = testRenamer({fn : newFile.base, ...restreamerOpts}, newFile.base.match(ro.regex)?.groups || {});
							return (parts.length===0 || parts.some(part => typeof part!=="string")) ? null : parts.join("");
						}
						catch
						{
							return null;
						}
					});

					xu.log4`Renamer #${i} produced: ${filenames}`;
					if(filenames.some(filename => typeof filename!=="string") || filenames.unique().length<filenames.length)
						continue;

					renamerNum = +i;
					renamer = testRenamer;
					break;
				}

				if(renamer===null)
				{
					xu.log2`${xu.c.blink + fg.pink("Failed")} to pick a renamer for ${f.files.new.length} files, keeping original names.`;
				}
				else
				{
					xu.log3`Picked renamer #${renamerNum} for renaming ${f.files.new.length} files...`;

					for(const newFile of f.files.new)
					{
						const replacementName = renamer({fn : newFile.base, ...restreamerOpts}, newFile.base.match(ro.regex)?.groups || {}).join("");
						xu.log2`${fg.orange(this.programid)} renaming output file ${newFile.base} to ${replacementName}`;
						await newFile.rename(replacementName, {replaceExisting : !!isChain});
					}
				}
			}
			else if(f.files.new.length===1)
			{
				const newFilename = newName + suffix + (ro.ext || f.new.ext);
				if(newFilename!==f.new.base)
				{
					xu.log2`${fg.orange(this.programid)} renaming single output file ${f.new.base} to ${newFilename}`;
					await f.new.rename(newFilename, {replaceExisting : !!isChain});
				}
			}
		}

		xu.log3`Program Result: ${r.pretty()}`;

		// if we have a disk quota, we need to make a temp out dir, rsync over our new files to it, unmount it and then rsync them back to the original outDir
		if(this.diskQuota)
		{
			const tmpOutDirPath = await fileUtil.genTempPath(f.root, "diskQuotaTmpOut");
			await Deno.mkdir(tmpOutDirPath, {recursive : true});
			const tmpF = await f.rsyncTo(tmpOutDirPath, {type : "new", relativeFrom : f.outDir.absolute});
			await runUtil.run("sudo", ["umount", f.outDir.absolute]);
			await tmpF.rsyncTo(f.outDir.absolute, {type : "new"});
			await fileUtil.unlink(tmpOutDirPath, {recursive : true});
			// don't need to do anything with the original f, everything should have the same path as before
		}

		// check to see if we need to chain to another program
		if(f.files.new?.length>0)
		{
			const chainParts = [];
			if(this.chain)
			{
				const chainResult = (typeof this.chain==="function" ? await this.chain(r) : this.chain);
				if(chainResult)
					chainParts.push(...chainResult.split("->"));
			}
			if(chain)
				chainParts.push(...chain.split("->"));

			if(chainParts.length>0)
			{
				for(const [, progRaw] of Object.entries(chainParts.map(v => v.trim())))
				{
					const newFiles = Array.from(f.files.new);
					const chainF = await f.clone();
					chainF.changeType("new", "prev");

					const handleNewFiles = async chainInputFiles =>
					{
						if(!chainF.new)
						{
							xu.log2`Chain ${progRaw} did ${fg.red("NOT")} produce any new files${xu.verbose<5 ? `, deleting ${chainInputFiles.length} chain input files!` : ""}`;
							if(xu.verbose<5)
							{
								for(const chainInputFile of chainInputFiles)
									await f.remove("new", chainInputFile, {unlink : true});
							}
							return;
						}

						xu.log3`Chain ${progRaw} resulted in new files: ${chainF.files.new.map(v => v.rel).join(" ")}`;

						// we used to check here if any of our new chain files already exist in f.new from a previous iteration, then we re-calculated our stats
						// however we now handle this automatically in FileSet.add when it already has the file it does a .calcStats() automatically
						// in the future though we could use this code here to help add collision avoidance
						//await (f.files.new || []).filter(v => chainF.files.new.some(oldNew => oldNew.rel===v.rel)).parallelMap(v => v.calcStats());
						
						await f.addAll("new", chainF.files.new);
						for(const inputFile of chainF.files.input)
						{
							if(!chainF.files.new.some(v => v.absolute===inputFile.absolute))
								await f.remove("new", inputFile, {unlink : true});
						}
						chainF.changeType("new", "prev");
					};
					
					const baseChainProgOpts = {isChain : true};

					// If we have just 1 file or we are taking multiple files and feeding them into 1 program, then we likely will have just 1 output file
					// So we set originalInput so it's named properly
					if(newFiles.length===1 || progRaw.startsWith("*"))
						baseChainProgOpts.originalInput = originalInput || f.input;

					if(progRaw.startsWith("*"))
					{
						chainF.removeType("input");
						await chainF.addAll("input", newFiles);

						xu.log3`Chaining to ${progRaw} with ${newFiles.length} files ${newFiles.map(newFile => newFile.rel).join(" ")}`;

						await Program.runProgram(progRaw.substring(1), chainF, baseChainProgOpts);
						await handleNewFiles(newFiles);
					}
					else
					{
						for(const newFile of newFiles)
						{
							const chainProgFlags = progRaw.startsWith("?") ? await this.chainCheck(r, newFile, progRaw.substring(1)) : {};
							if(!chainProgFlags)
								continue;
							
							const chainProgOpts = {...baseChainProgOpts};
							if(Object.isObject(chainProgFlags))
								chainProgOpts.flags = chainProgFlags;

							chainF.removeType("input");
							await chainF.add("input", newFile);

							xu.log3`Chaining to ${progRaw} with file ${newFile.rel}`;

							await Program.runProgram(progRaw.startsWith("?") ? progRaw.substring(1) : progRaw, chainF, chainProgOpts);
							await handleNewFiles([newFile]);
						}
					}
				}
			}
		}

		return r;
	}

	// runs the programid program
	static async runProgram(progRaw, fRaw, progOptions={})
	{
		if(progRaw.includes("->"))
		{
			const chainParts = progRaw.split("->");
			progOptions.chain = chainParts.slice(1).join("->");
			progRaw = chainParts[0].trim();	// eslint-disable-line no-param-reassign
		}

		const {programid, flagsRaw=""} = progRaw.match(/^\s*(?<programid>[^[]+)(?<flagsRaw>.*)$/).groups;
		const flags = Object.fromEntries((flagsRaw.match(/\[[^:\]]+:?[^\]]*]/g) || []).map(flag =>
		{
			const {name, val} = flag.match(/\[(?<name>[^:\]]+):?(?<val>[^\]]*)]/)?.groups || {};
			return (name ? [name, (val.length>0 ? (val.isNumber() ? +val : val) : true)] : null);
		}).filter(v => !!v).filter(([name, val]) =>
		{
			// see if any of the flags are actually programOptions
			if(["suffix"].includes(name))
			{
				progOptions[name] = val;
				return false;
			}

			return true;
		}));

		// run prog
		if(!progOptions.flags)
			progOptions.flags = {};
		Object.assign(progOptions.flags, flags);

		const {programs} = await import("./program/programs.js");
		const program = programs[programid];
		if(!program)
			throw new Error(`Unknown programid: ${programid}`);

		let f = fRaw;

		// if fRaw isn't a FileSet, then we will create a temporary one
		if(!(fRaw instanceof FileSet))
		{
			const inputFile = fRaw instanceof DexFile ? fRaw.clone() : await DexFile.create(fRaw);
			f = await FileSet.create(inputFile.root, "input", inputFile);
			
			const outDirPath = await fileUtil.genTempPath(undefined, `${programid}-out`);
			await Deno.mkdir(outDirPath, {recursive : true});
			await f.add("outDir", outDirPath);

			const homeDirPath = await fileUtil.genTempPath(undefined, `${programid}-home`);
			await Deno.mkdir(homeDirPath, {recursive : true});
			await f.add("homeDir", homeDirPath);
		}

		xu.log5`Program ${progRaw} converted to ${progOptions}`;
		
		return program.run(f, progOptions);
	}

	// forms a path to dexvert/bin/{rel}
	static binPath(rel)
	{
		return path.join(xu.dirname(import.meta), "..", "bin", rel);
	}
}
