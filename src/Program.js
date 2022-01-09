import {xu, fg} from "xu";
import {XLog} from "xlog";
import {fileUtil, runUtil} from "xutil";
import {path} from "std";
import {validateClass, validateObject} from "validator";
import {RunState} from "./RunState.js";
import {FileSet} from "./FileSet.js";
import {DexFile} from "./DexFile.js";
import {run as runDOS} from "./dosUtil.js";
import {run as runQEMU, QEMUIDS} from "./qemuUtil.js";

const DEFAULT_TIMEOUT = xu.MINUTE*5;
const DEFAULT_FLAGS = ["filenameEncoding", "renameOut"];
const GLOBAL_FLAGS = {};
export {GLOBAL_FLAGS};

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
			renameOut : {types : ["function", Object, "boolean"], required : true},

			// meta
			flags        : {type : Object},
			notes        : {type : "string"},
			package      : {types : ["string", Array]},
			runOptions   : {types : [Object, "function"]},
			unsafe       : {type : "boolean"},
			website      : {type : "string", url : true},

			// execution
			args             : {type : "function", length : [0, 1]},
			allowDupOut      : {type : "boolean"},
			bin              : {type : "string"},
			chain            : {types : ["function", "string"]},
			chainCheck       : {type : "function", length : [0, 3]},
			checkForDups     : {type : "boolean"},
			cwd              : {type : "function", length : [0, 1]},
			diskQuota        : {type : "number", range : [1]},
			dosData          : {types : ["function", Object]},
			exec             : {type : "function", length : [0, 1]},
			filenameEncoding : {types : ["function", "string"]},
			mirrorInToCWD    : {types : ["boolean", "string"]},
			outExt           : {types : ["function", "string"]},
			post             : {type : "function", length : [0, 1]},
			postExec         : {type : "function", length : [0, 1]},
			pre              : {type : "function", length : [0, 1]},
			qemuData         : {types : ["function", Object]},
			renameIn         : {type : "boolean"},
			verify           : {type : "function", length : [0, 2]}
		});

		if(program.renameOut && Object.isObject(program.renameOut))
		{
			validateObject(program.renameOut, {
				ext          : {types : ["string", "function"]},
				name         : {types : ["boolean", "string", "function"]},
				regex        : {type : RegExp},
				renamer      : {type : ["function"]},
				alwaysRename : {type : "boolean"},
				preSensitive : {type : "boolean"}
			});
		}

		return program;
	}

	// runs the current program with the given input and output FileSets and various options
	async run(f, {timeout=DEFAULT_TIMEOUT, flags={}, originalInput, chain, suffix="", isChain, format, xlog=new XLog()}={})
	{
		flags = {...flags, ...GLOBAL_FLAGS[this.programid]};	// eslint-disable-line no-param-reassign
		if(!(f instanceof FileSet))
			throw new Error(`Program ${fg.orange(this.programid)} run didn't get a FileSet as arg 1`);
		
		const unknownFlags = Object.keys(flags).subtractAll([...DEFAULT_FLAGS, ...Object.keys(this.flags || {})]);
		if(unknownFlags.length>0)
			throw new Error(`Program ${fg.orange(this.programid)} run got unknown flags: ${unknownFlags.join(" ")}`);
		
		// restrict the size of our out dir by mounting a RAM disk of a static size to it, that way we can't fill up our entire hard drive with misbehaving programs
		if(this.diskQuota)
			await runUtil.run("sudo", ["mount", "-t", "tmpfs", "-o", `size=${this.diskQuota},mode=0777,nodev,noatime`, "tmpfs", f.outDir.absolute]);

		// create a RunState to store program results/meta
		const r = RunState.create({programid : this.programid, f, flags, xlog});
		r.cwd = f.root;
		if(originalInput)
			r.originalInput = originalInput;
		if(this.cwd)
		{
			const newCWD = await this.cwd(r);
			r.cwd = newCWD.startsWith("/") ? newCWD : path.resolve(f.root, newCWD);
		}

		if(this.mirrorInToCWD)
		{
			if(this.mirrorInToCWD==="copy")	// eslint-disable-line unicorn/prefer-ternary
				await runUtil.run("rsync", [path.join(r.cwd, r.inFile()), path.join(r.cwd, path.basename(r.inFile()))]);
			else
				await Deno.symlink(path.join(r.cwd, r.inFile()), path.join(r.cwd, path.basename(r.inFile())));
			r.mirrorInToCWD = true;
		}

		if(this.pre)
			await this.pre(r);

		if(this.exec)
		{
			// run arbitrary javascript code
			xlog.info`Program ${fg.orange(this.programid)} executing ${".exec"} steps`;
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
			if(this.runOptions)
				Object.assign(r.runOptions, typeof this.runOptions==="function" ? await this.runOptions(r) : this.runOptions);

			xlog.info`Program ${fg.orange(this.programid)}${Object.keys(flags).length>0 ? Object.entries(flags).map(([k, v]) => xu.bracket(`${k}:${v}`)).join("") : ""} running as \`${this.bin} ${r.args.map(arg => (arg.includes(" ") ? `"${arg}"` : arg)).join(" ")}\``;
			xlog.debug`  with options ${xu.inspect(r.runOptions).squeeze()}`;
			const {stdout, stderr, status} = await runUtil.run(this.bin, r.args, r.runOptions);
			Object.assign(r, {stdout, stderr, status});
		}
		else if(this.loc==="dos")
		{
			r.dosData = {root : f.root, cmd : this.bin, xlog};
			r.dosData.args = this.args ? await this.args(r) : [];
			if(this.dosData)
				Object.assign(r.dosData, typeof this.dosData==="function" ? await this.dosData(r) : this.dosData);

			r.status = await runDOS(r.dosData);
		}
		else if(QEMUIDS.includes(this.loc))
		{
			r.qemuData = {f, cmd : this.bin, osid : this.loc, xlog};
			r.qemuData.args = this.args ? await this.args(r) : [];
			if(this.qemuData)
				Object.assign(r.qemuData, typeof this.qemuData==="function" ? await this.qemuData(r) : this.qemuData);

			r.status = await runQEMU(r.qemuData);
		}

		if(this.postExec)
		{
			try { await this.postExec(r); }
			catch(err) { xlog.error`Program postExec ${fg.orange(this.programid)} threw error ${err}`; }
		}

		if(this.mirrorInToCWD)
			await fileUtil.unlink(r.inFile({absolute : true}));

		// some programs like resource_dasm will DELETE the output directory if it wasn't able to extract, so we should check that it still exists
		if(f.outDir && await fileUtil.exists(f.outDir.absolute))
		{
			// we may have new files on disk in f.outDir

			// first we have to run fixPerms in order to ensure we can access the new files
			xlog.trace`Program ${fg.orange(this.programid)} fixing permissions...`;
			await runUtil.run(Program.binPath("fixPerms"), [], {cwd : f.outDir.absolute});

			// next we fix any filenames that contain UTF16 or other non-UTF8 characters, converting them to UTF8. This fixes problems with tree/readdir etc. because deno only supports UTF8 encodings
			// can run `convmv --list` for a list of valid encoding names
			xlog.trace`Program ${fg.orange(this.programid)} fixing filename encoding...`;
			const targetEncoding = (flags.filenameEncoding || (typeof this.filenameEncoding==="function" ? await this.filenameEncoding(r) : this.filenameEncoding)) || "windows-1252";
			await runUtil.run("convmv", ["-r", "--qfrom", "--qto", "--notest", "-f", targetEncoding, "-t", "UTF-8", f.outDir.absolute]);

			// delete empty files/broken symlinks. find is very fast at this, so use that
			xlog.trace`Program ${fg.orange(this.programid)} deleting empty files and broken symlinks...`;
			await runUtil.run("find", [f.outDir.absolute, "-type", "f", "-empty", "-delete"]);
			await runUtil.run("find", [f.outDir.absolute, "-xtype", "l", "-delete"]);

			// also delete any 'special' files that may be dangerous to process. block special, character special named pipe, socket
			xlog.trace`Program ${fg.orange(this.programid)} deleting special files...`;
			await runUtil.run("find", [f.outDir.absolute, "-type", "b,c,p,s", "-delete"]);

			// now find any new files on disk in the output dir that we don't yet
			xlog.trace`Program ${fg.orange(this.programid)} locating new files...`;
			const newFilePaths = (await fileUtil.tree(f.outDir.absolute, {nodir : true})).subtractAll([...(f.files.output || []), ...(f.files.prev || []), ...(f.files.new || [])].map(v => v.absolute));

			xlog.trace`Program ${fg.orange(this.programid)} doing first pass on ${newFilePaths.length} new files...`;
			await newFilePaths.parallelMap(async newFilePath =>
			{
				const newFileRel = path.relative(f.outDir.absolute, newFilePath);

				const newFile = await DexFile.create({root : f.root, absolute : newFilePath});

				// If we are a symlink, we need to make sure we are not pointing outside of our directory
				if(newFile.isSymlink)
				{
					let linkPath = await Deno.readLink(newFilePath);
					if(!linkPath.startsWith("/"))
						linkPath = path.join(path.dirname(newFilePath), linkPath);
					const linkPathRel = path.relative(f.outDir.absolute, linkPath);
					if(linkPathRel.startsWith("../"))
					{
						xlog.warn`Program ${fg.orange(this.programid)} deleting output symlink ${newFileRel} due to linking to a file outside of the output dir: ${linkPath}`;
						await fileUtil.unlink(newFilePath);
						return;
					}

					if((await Deno.lstat(linkPath)).isDirectory)
					{
						xlog.warn`Program ${fg.orange(this.programid)} deleting output symlink ${newFileRel} due to being a dir link, which can cause infinite loops and won't result in new files: ${path.basename(newFilePath)} -> ${linkPathRel}`;
						await fileUtil.unlink(newFilePath);
						return;
					}
				}

				// some programs (such as mounting archive/rawPartition/Madame X Game.bin) leaves files with an epoch timestamp. If this happens reset it to input file date
				if(newFile.ts===0)
				{
					if(newFile.isSymlink)	// eslint-disable-line unicorn/prefer-ternary
						await runUtil.run("touch", ["-h", "-d", new Date((originalInput || f.input).ts).toISOString(), newFile.absolute]);	// to change symlink date we have leave deno and touch it
					else
						await newFile.setTS((originalInput || f.input).ts);
				}

				// if this program has a custom verification step, check that
				if(this.verify && !(await this.verify(r, newFile)))
				{
					xlog.warn`Program ${fg.orange(this.programid)} deleting output file ${newFileRel} due to failing program.verify() function`;
					await fileUtil.unlink(newFilePath);
					return;
				}

				// check to see if the resulting file is identical to our input file (sample/executable/exe/Oidata)
				// we always check if we have just 1 output file, otherwise we only check if checkForDups is set
				if(!this.allowDupOut && (this.checkForDups || newFilePaths.length===1) && await fileUtil.areEqual(newFilePath, f.input.absolute))
				{
					xlog.warn`Program ${fg.orange(this.programid)} deleting output file ${newFileRel} due to being identical to input file ${f.input.pretty()}`;
					await fileUtil.unlink(newFilePath);
					return;
				}

				// add our new file to our fileset
				await f.add("new", newFile);
			});
		}

		// sort the filenames by depth and then by filename
		if(f.files.new)
		{
			xlog.debug`Program ${fg.orange(this.programid)} located ${f.files.new.length} new files...`;
			f.files.new.sortMulti([file => file.rel.split("/").length, file => file.base]);
		}

		if(this.post)
		{
			try { await this.post(r); }
			catch(err) { xlog.error`Program post ${fg.orange(this.programid)} threw error ${err}`; }
		}

		const renameOut = Object.hasOwn(flags, "renameOut") ? flags.renameOut : (typeof this.renameOut==="function" ? await this.renameOut(r) : this.renameOut);

		// if we have some new files, time to rename them
		if(f.outDir && f.files.new?.length && renameOut!==false)
		{
			const ro = Object.assign({ext : typeof this.outExt==="function" ? await this.outExt(r) || "" : this.outExt || "", name : true}, Object.isObject(renameOut) ? renameOut : {});
			if(Object.isObject(renameOut) && renameOut.preSensitive)
			{
				if(!renameOut.name)
					ro.name = (ignored, oi) => (oi.name.length<=3 && oi.preName.length>oi.name.length ? oi.preName : oi.name);
				if(!renameOut.ext)
					ro.ext = (ignored, oi) => (oi.name.length<=3 && oi.preName.length>oi.name.length ? oi.preExt : "");
			}

			const getName = o =>
			{
				// some files have the extension on the front of the file, like amiga with music/mod/mod.africa, we already set this in DexFile.preName
				// so if in our format.ext we have our name, then use preName as our name (unless preName is also in ext, then stick with name)
				if(o.preName?.length && (format?.ext || []).some(ext => ext.toLowerCase()===`.${o.name.toLowerCase()}`) && !(format?.ext || []).some(ext => ext.toLowerCase()===`.${o.preName.toLowerCase()}`))
					return o.preName;

				return o.name;
			};
			const newName = (ro.name===true ? getName(originalInput || f.input) : ((typeof ro.name==="function" ? ro.name(r, originalInput) : ro.name) || getName(f.new)));
			const newExt = ((typeof ro.ext==="function" ? ro.ext(r, originalInput) : ro.ext) || f.new.ext);
			const originalExt = originalInput ? originalInput.ext : null;
			const restreamerOpts = {r, newName, newExt, suffix, numFiles : f.files.new.length, originalExt};

			// See if we have more advanced renaming
			if(ro.renamer && (f.files.new.length>1 || ro.alwaysRename))
			{
				let renamer = null;
				let renamerNum = null;
				for(const [i, testRenamer] of Object.entries(ro.renamer))
				{
					const filenames = f.files.new.map(newFile =>
					{
						try
						{
							const parts = testRenamer({fn : newFile.base, ...restreamerOpts}, (ro.regex ? (newFile.base.match(ro.regex)?.groups || {}) : {}));
							return (parts.length===0 || parts.some(part => typeof part!=="string")) ? null : parts.join("");
						}
						catch
						{
							return null;
						}
					});

					xlog.debug`Renamer #${i} produced: ${filenames}`;
					if(filenames.some(filename => typeof filename!=="string") || filenames.unique().length<filenames.length)
						continue;

					renamerNum = +i;
					renamer = testRenamer;
					break;
				}

				if(renamer===null)
				{
					xlog.warn`${xu.c.blink + fg.pink("Failed")} to pick a renamer for ${f.files.new.length} files, keeping original names.`;
				}
				else
				{
					xlog.info`Picked renamer #${renamerNum} for renaming ${f.files.new.length} files...`;

					for(const newFile of f.files.new)
					{
						const replacementName = renamer({fn : newFile.base, ...restreamerOpts}, newFile.base.match(ro.regex)?.groups || {}).join("");
						xlog.warn`${fg.orange(this.programid)} renaming output file ${newFile.base} to ${replacementName}`;
						await newFile.rename(replacementName, {replaceExisting : !!isChain});
					}
				}
			}
			else if(f.files.new.length===1)
			{
				const newFilename = newName + suffix + newExt;
				if(newFilename!==f.new.base)
				{
					xlog.warn`${fg.orange(this.programid)} renaming single output file ${f.new.base} to ${newFilename}`;
					await f.new.rename(newFilename, {replaceExisting : !!isChain});
				}
			}
		}

		xlog.info`Program Result: ${r.pretty()}`;

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
				const chainOutput = (typeof this.chain==="function" ? await this.chain(r) : this.chain);
				if(chainOutput)
					chainParts.push(...chainOutput.split("->"));
			}
			if(chain)
				chainParts.push(...chain.split("->"));

			if(chainParts.length>0)
			{
				for(const [, progRaw] of Object.entries(chainParts.map(v => v.trim())))
				{
					const handleNewFiles = async (chainResult, inputFiles) =>
					{
						if(!chainResult || !chainResult.f.new)
						{
							xlog.warn`Chain ${progRaw} did ${fg.red("NOT")} produce any new files!`;
							if(!xlog.atLeast("trace"))
							{
								await chainResult.unlinkHomeOut();
								
								xlog.info`Deleting ${inputFiles.length} chain input files!`;
								for(const inputFile of inputFiles)
									await f.remove("new", inputFile, {unlink : true});
							}
							return;
						}

						// copy our new files over to our out dir. WARNING! This doesn't do ANY collision avoidance at all, so if there are duplicate filenames, they will overwrite the existing files
						const newFileSet = await chainResult.f.rsyncTo(f.outDir.absolute, {type : "new", relativeFrom : chainResult.f.outDir.absolute});
						newFileSet.changeRoot(f.root);
						await f.addAll("new", newFileSet.files.new);

						// remove any old input files that are not part of our new chain output/new files
						for(const inputFile of inputFiles)
						{
							if(!newFileSet.files.new.some(v => v.absolute===inputFile.absolute))
								await f.remove("new", inputFile, {unlink : true});
						}

						xlog.info`Chain ${progRaw} resulted in new files: ${newFileSet.files.new.map(v => v.rel).join(" ")}`;

						await chainResult.unlinkHomeOut();
					};
					
					const baseChainProgOpts = {isChain : true, format, xlog};
					const newFiles = Array.from(f.files.new);

					// If we have just 1 file or we are taking multiple files and feeding them into 1 program, then we likely will have just 1 output file
					// So we set originalInput so it's named properly
					// Don't do this though if the current program has a custom renamer with alwaysRename set
					if((newFiles.length===1 && !renameOut?.alwaysRename) || progRaw.startsWith("*"))
					{
						if(newFiles.length===1 && renameOut===false)	// eslint-disable-line unicorn/prefer-ternary
						{
							// if only 1 output file and we were instructed to NOT rename anything, then we should TRUST the newFile name and chain that as the original input
							baseChainProgOpts.originalInput = newFiles[0];
						}
						else
						{
							// otherwise the originalInput should be set to either our very originalInput file or our current f.input
							baseChainProgOpts.originalInput = originalInput || f.input;
						}
					}

					if(progRaw.startsWith("*"))
					{
						xlog.info`Chaining to ${progRaw} with ${newFiles.length} files ${newFiles.map(newFile => newFile.rel).join(" ")}`;
						await handleNewFiles(await Program.runProgram(progRaw.substring(1), newFiles, baseChainProgOpts), newFiles);
					}
					else
					{
						await newFiles.parallelMap(async newFile =>
						{
							// if chain starts with a question mark ? then we need to have a truthy response from chainCheck() in order to proceed with chaining this file
							const {programid : chainProgramid} = Program.parseProgram(progRaw.substring(1));
							const chainProgFlags = progRaw.startsWith("?") ? await this.chainCheck(r, newFile, chainProgramid) : {};
							if(!chainProgFlags)
								return;

							const chainProgOpts = {...baseChainProgOpts};
							if(Object.isObject(chainProgFlags))
								chainProgOpts.flags = chainProgFlags;

							xlog.info`Chaining to ${progRaw} with file ${newFile.rel}`;
							await handleNewFiles(await Program.runProgram(progRaw.startsWith("?") ? progRaw.substring(1) : progRaw, newFile, chainProgOpts), [newFile]);
						});	// chain 10 output files at once, or 33% of OS CPU count, whichever is smaller
					}
				}
			}
		}

		return r;
	}

	// runs the programid program
	static async runProgram(progRaw, fRaw, _progOptions={})
	{
		const progOptions = Object.assign({}, _progOptions);
		const xlog = progOptions.xlog;
		if(!xlog)
			throw new Error("Required xlog param for runProgram not found");
		if(progRaw.includes("->"))
		{
			const chainParts = progRaw.split("->");
			progOptions.chain = chainParts.slice(1).join("->");
			progRaw = chainParts[0].trim();	// eslint-disable-line no-param-reassign
		}

		const {programid, flags, progOptions : moreProgOptions} = Program.parseProgram(progRaw);
		Object.assign(progOptions, moreProgOptions);

		// run prog
		if(!progOptions.flags)
			progOptions.flags = {};
		Object.assign(progOptions.flags, flags);

		const {programs} = await import("./program/programs.js");
		const program = programs[programid];
		if(!program)
			throw new Error(`Unknown programid: ${programid}`);

		let f = fRaw;

		let srcFiles = null;
		let safeFiles = null;

		// if fRaw isn't a FileSet, then we will create a temporary one
		if(!(fRaw instanceof FileSet))
		{
			if(!Array.force(fRaw).every(v => v instanceof DexFile))
				throw new Error("You must pass either a FileSet, DexFile or array of DexFiles to Program.runProgram");

			const isFilenameSafe = filename =>
			{
				// if anything non-printable, fail
				if(filename.length!==filename.replace(/[^ -~]/, "").length)
					return false;
				
				// backslash, fail
				if(filename.includes("\\"))
					return false;

				// if the first character is anything other than A-Z a-z 0-9 _
				if(!(/\w/).test(filename.at(0)))
					return false;

				return true;
			};

			srcFiles = Array.force(fRaw);
			if(program.renameIn!==false && !progOptions.skipSafeRename)
			{
				safeFiles = await srcFiles.parallelMap(async srcFile =>
				{
					if(isFilenameSafe(srcFile.base))
						return srcFile;
					
					const safeFilename = path.basename(await fileUtil.genTempPath(srcFile.dir, srcFile.ext.replace(/[^ -~]/, "")));
					xlog.info`Program ${progRaw} safe renaming ${srcFile.base} to ${safeFilename}`;
					const safeFile = srcFile.clone();
					await safeFile.rename(safeFilename);
					return safeFile;
				});

				if(safeFiles.length===1 && !progOptions.originalInput)
					progOptions.originalInput = srcFiles[0];
			}

			f = await FileSet.create(srcFiles[0].root, "input", safeFiles || srcFiles);
			
			const outDirPath = await fileUtil.genTempPath(undefined, `${programid}_out`);
			await Deno.mkdir(outDirPath, {recursive : true});
			await f.add("outDir", outDirPath);

			const homeDirPath = await fileUtil.genTempPath(undefined, `${programid}_home`);
			await Deno.mkdir(homeDirPath, {recursive : true});
			await f.add("homeDir", homeDirPath);
		}

		if(progOptions.outFile)
			await f.add("outFile", progOptions.outFile);

		const debugPart = Object.assign({}, progOptions);
		delete debugPart.xlog;
		xlog.trace`Program ${progRaw} converted to ${debugPart} with f ${f}`;
		
		const programResult = await program.run(f, progOptions);

		if(srcFiles && safeFiles)
		{
			await safeFiles.parallelMap(async (safeFile, i) =>
			{
				const srcFile = srcFiles[i];
				if(safeFile.absolute===srcFile.absolute)
					return;
				
				if(!(await fileUtil.exists(safeFile.absolute)))
				{
					xlog.info`Program ${progRaw} safe path no longer exists ${safeFile.pretty()}`;
					return;
				}
				
				xlog.info`Program ${progRaw} safe reverting ${safeFile.base} to ${srcFile.base}`;
				await safeFile.rename(srcFile.base);
			});
		}

		if(progOptions.autoUnlink && !(fRaw instanceof FileSet))
			await programResult.unlinkHomeOut();

		return programResult;
	}

	static parseProgram(progRaw)
	{
		const progOptions = {};
		const {programid, flagsRaw=""} = progRaw.match(/^\s*(?<programid>[^[]+)(?<flagsRaw>.*)$/).groups;
		const flags = {};
		
		// We used to do an more succint Object.fromEntries() but beause we can have duplicate flag names which should be turned into an array (deark[opt:*][opt:*]) we have to do it this way
		(flagsRaw.match(/\[[^:\]]+:?[^\]]*]/g) || []).forEach(flag =>
		{
			const {name, val} = flag.match(/\[(?<name>[^:\]]+):?(?<val>[^\]]*)]/)?.groups || {};
			if(!name)
				return;

			const valFinal = (val.length>0 ? (val.isNumber() ? +val : (["true", "false"].includes(val) ? val==="true" : val)) : true);

			// see if any of the flags are actually programOptions
			if(["suffix"].includes(name))
			{
				progOptions[name] = valFinal;
				return;
			}

			if(!Object.hasOwn(flags, name))
				flags[name] = valFinal;
			else if(Array.isArray(flags[name]))
				flags[name].push(valFinal);
			else
				flags[name] = [flags[name], valFinal];
		});

		return {programid, flags, progOptions};
	}

	static async hasProgram(progRaw)
	{
		const {programs} = await import("./program/programs.js");
		const {programid} = Program.parseProgram(progRaw);
		return Object.hasOwn(programs, programid);
	}

	// forms a path to dexvert/bin/{rel}
	static binPath(rel)
	{
		return path.join(xu.dirname(import.meta), "..", "bin", rel);
	}

	// returns args needed to call a sub deno script
	static denoArgs(...args)
	{
		return ["run", "--import-map", "/mnt/compendium/DevLab/deno/importMap.json", "--no-check", "--unstable", "--allow-read", "--allow-write", "--allow-env", "--allow-run", ...args];
	}

	// returns env needed to properly run deno scripts
	static denoEnv()
	{
		return {DENO_DIR : "/mnt/compendium/.deno"};
	}
}
