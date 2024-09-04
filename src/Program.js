import {xu, fg} from "xu";
import {XLog} from "xlog";
import {fileUtil, runUtil, sysUtil, printUtil} from "xutil";
import {path} from "std";
import {validateClass, validateObject} from "validator";
import {RunState} from "./RunState.js";
import {FileSet} from "./FileSet.js";
import {DexFile} from "./DexFile.js";
import {run as runDOS} from "./dosUtil.js";
import {run as runOS, OSIDS} from "./osUtil.js";
import {run as runWine, WINE_WEB_HOST, WINE_WEB_PORT} from "./wineUtil.js";
import {programs} from "./program/programs.js";
import {DEXRPC_HOST, DEXRPC_PORT} from "./dexUtil.js";

const MAX_FILENAME_LENGTH = 245;
const DEFAULT_TIMEOUT = xu.MINUTE*5;
const GLOBAL_FLAGS = ["bulkCopyOut", "filenameEncoding", "forbidChildRun", "forbiddenMagic", "hasExtMatch", "matchType", "noAux", "osHint", "osPriority", "renameKeepFilename", "renameOut", "skipVerify", "strongMatch", "subOutDir"];

// A global variable that contains certain flags and properties to adhere to until clearRuntime is called
const RUNTIME =
{
	globalFlags   : {},
	forbidProgram : new Set()
};
export {RUNTIME};

export function clearRuntime()
{
	Object.clear(RUNTIME.globalFlags);
	RUNTIME.forbidProgram.clear();
	delete RUNTIME.asFormat;
}

const CONVERT_PNG_ARGS = ["-strip", "-define", "filename:literal=true", "-define", "png:exclude-chunks=time"];
export {CONVERT_PNG_ARGS};

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
			loc       : {type : "string", required : true, enum : ["local", "dos", "wine", ...OSIDS]},
			renameOut : {types : ["function", Object, "boolean"], required : true},

			// meta
			classify   : {type : "boolean"},
			flags      : {type : Object},
			exclusive  : {type : "string"},
			notes      : {type : "string"},
			package    : {types : ["string", Array]},
			runOptions : {types : [Object, "function"]},
			unsafe     : {type : "boolean"},
			website    : {type : "string", url : true},

			// execution
			args             : {type : "function", length : [0, 1]},
			allowDupOut      : {type : "boolean"},
			bin              : {types : ["function", "string"]},
			bruteFlags       : {type : Object},
			chain            : {types : ["function", "string"]},
			chainCheck       : {type : "function", length : [0, 3]},
			chainFailKeep    : {type : "function", length : [0, 4]},
			chainPost        : {type : "function", length : [0, 1]},
			checkForDups     : {type : "boolean"},
			failOnDups       : {type : "boolean"},
			forbidChildRun   : {type : "boolean"},
			cwd              : {type : "function", length : [0, 1]},
			diskQuota        : {types : ["function", "number"]},
			dosData          : {types : ["function", Object]},
			wineData         : {types : ["function", Object]},
			osData           : {types : ["function", Object]},
			exec             : {type : "function", length : [0, 1]},
			filenameEncoding : {types : ["function", "string"]},
			mirrorInToCWD    : {types : ["boolean", "string"]},
			outExt           : {types : ["function", "string"]},
			post             : {type : "function", length : [0, 2]},
			postExec         : {type : "function", length : [0, 1]},
			pre              : {type : "function", length : [0, 1]},
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

		if(program.wineData?.script && !program.exclusive)
			throw new Error(`Program ${fg.orange(program.programid)} has a wineData.script but is not marked exclusive, which is needed to work correctly in parallel executions`);

		return program;
	}

	// runs the current program with the given input and output FileSets and various options
	async run(f, {timeout=DEFAULT_TIMEOUT, flags={}, originalInput, chain, suffix="", isChain, chainParent, format, xlog=new XLog()}={})
	{
		flags = {...flags, ...RUNTIME.globalFlags[this.programid]};
		if(!(f instanceof FileSet))
			throw new Error(`Program ${fg.orange(this.programid)} run didn't get a FileSet as arg 1`);
		
		const unknownFlags = Object.keys(flags).subtractAll([...GLOBAL_FLAGS, ...Object.keys(this.flags || {})]);
		if(unknownFlags.length>0)
			throw new Error(`Program ${fg.orange(this.programid)} run got unknown flags: ${unknownFlags.join(" ")}`);
		
		// create a RunState to store program results/meta
		const r = RunState.create({programid : this.programid, f, flags, xlog});
		r.cwd = f.root;
		if(chainParent)
			r.chainParent = chainParent;
		if(originalInput)
			r.originalInput = originalInput;
		if(this.cwd)
		{
			const newCWD = await this.cwd(r);
			r.cwd = newCWD.startsWith("/") ? newCWD : path.resolve(f.root, newCWD);
		}

		// restrict the size of our out dir by mounting a RAM disk of a static size to it, that way we can't fill up our entire hard drive with misbehaving programs
		if(this.diskQuota)
			await runUtil.run("sudo", ["mount", "-t", "tmpfs", "-o", `size=${typeof this.diskQuota==="function" ? await this.diskQuota(r) : this.diskQuota},mode=0777,nodev,noatime`, "tmpfs", f.outDir.absolute]);

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

		const getBin = async () => (typeof this.bin==="function" ? await this.bin(r) : this.bin);
		const getArgs = async () => (this.args ? await this.args(r) : []).map(arg => arg.toString());

		if(this.exclusive)
		{
			xlog.debug`Program ${fg.orange(this.programid)} waiting for lock...`;
			await xu.waitUntil(async () => (await (await fetch(`http://${DEXRPC_HOST}:${DEXRPC_PORT}/lock`, {method : "POST", headers : { "content-type" : "application/json" }, body : JSON.stringify({lockid : this.exclusive})}))?.text())==="true");
		}

		try
		{
			if(this.exec)
			{
				// run arbitrary javascript code
				xlog.info`Program ${fg.orange(this.programid)} executing ${".exec"} steps`;
				await this.exec(r);
			}
			else if(this.loc==="local")
			{
				// run a program on disk
				r.bin = await getBin();
				r.args = await getArgs();
				r.runOptions = {cwd : r.cwd, timeout};
				if(f.homeDir)
					r.runOptions.env = {HOME : f.homeDir.absolute};
				if(this.runOptions)
					Object.assign(r.runOptions, typeof this.runOptions==="function" ? await this.runOptions(r) : this.runOptions);

				xlog.info`Program ${fg.orange(this.programid)}${Object.keys(flags).length>0 ? Object.entries(flags).map(([k, v]) => xu.bracket(`${k}:${v}`)).join("") : ""} running as \`${this.bin} ${r.args.map(arg => (arg.includes(" ") ? `"${arg}"` : arg)).join(" ")}\``;
				xlog.debug`  with options ${printUtil.inspect(r.runOptions).squeeze()}`;
				const {stdout, stderr, status} = await runUtil.run(this.bin, r.args, r.runOptions);
				Object.assign(r, {stdout, stderr, status});
			}
			else if(this.loc==="dos")
			{
				r.dosData = {root : f.root, outDir : r.f.outDir, cmd : await getBin(), xlog};
				r.dosData.args = await getArgs();
				if(this.dosData)
					Object.assign(r.dosData, typeof this.dosData==="function" ? await this.dosData(r) : this.dosData);

				r.status = await runDOS(r.dosData);
			}
			else if(this.loc==="wine")
			{
				r.wineCounter = +(await (await fetch(`http://${WINE_WEB_HOST}:${WINE_WEB_PORT}/getWineCounter`)).text());	// we don't use xu.randStr() because we append to c:\out<counter> and thus need full path to be < 8 chars
				r.wineData = {f, cmd : await getBin(), cwd : r.cwd, xlog, wineCounter : r.wineCounter};
				r.wineData.args = await getArgs();
				if(this.wineData)
					Object.assign(r.wineData, typeof this.wineData==="function" ? await this.wineData(r) : this.wineData);

				r.status = await runWine(r.wineData);
			}
			else if(OSIDS.includes(this.loc))
			{
				r.osData = {f, cmd : await getBin(), osid : this.loc, xlog};
				if(format?.formatid)
					r.osData.meta = `${format.familyid}/${format.formatid}`;
				r.osData.args = await getArgs();
				if(this.osData)
					Object.assign(r.osData, typeof this.osData==="function" ? await this.osData(r) : this.osData);

				r.status = await runOS(r.osData);
			}

			if(this.postExec)
				await this.postExec(r);
		}
		catch(err)
		{
			xlog.error`Program ${fg.orange(this.programid)} execution threw error ${err}`;
		}

		if(this.exclusive)
		{
			xlog.debug`Program ${fg.orange(this.programid)} releasing lock...`;
			await xu.waitUntil(async () => (await (await fetch(`http://${DEXRPC_HOST}:${DEXRPC_PORT}/unlock`, {method : "POST", headers : { "content-type" : "application/json" }, body : JSON.stringify({lockid : this.exclusive})}))?.text())==="true");
		}

		if(this.mirrorInToCWD)
			await fileUtil.unlink(r.inFile({absolute : true}));

		// some programs like resource_dasm will DELETE the output directory if it wasn't able to extract, so we should check that it still exists
		if(f.outDir && await fileUtil.exists(f.outDir.absolute))
		{
			// we may have new files on disk in f.outDir

			// first we have to run fixPerms in order to ensure we can access the new files
			xlog.info`Program ${fg.orange(this.programid)} fixing permissions for: ${f.outDir.absolute}...`;
			await runUtil.run("/mnt/compendium/bin/fixPerms", [], {cwd : f.outDir.absolute, liveOutput : true});

			// next we fix any filenames that contain UTF16 or other non-UTF8 characters, converting them to UTF8. This fixes problems with tree/readdir etc. because deno only supports UTF8 encodings
			// can run `convmv --list` for a list of valid encoding names
			xlog.debug`Program ${fg.orange(this.programid)} fixing filename encoding...`;
			const targetEncoding = (flags.filenameEncoding || (typeof this.filenameEncoding==="function" ? await this.filenameEncoding(r) : this.filenameEncoding)) || "windows-1252";
			await runUtil.run("convmv", ["-r", "--qfrom", "--qto", "--notest", "-f", targetEncoding, "-t", "UTF-8", f.outDir.absolute]);

			// delete various things
			xlog.debug`Program ${fg.orange(this.programid)} deleting directory symlinks, empty files, 'special' files, and broken symlinks...`;
			await runUtil.run("find", [f.outDir.absolute, "-type", "l", "-xtype", "d", "-delete"]);		// delete directory symlinks, which are dangerous as they could point outside of the output directory
			await runUtil.run("find", [f.outDir.absolute, "-type", "b,c,p,s", "-delete"]);				// delete special files like block, named pipes, sockets, etc
			await runUtil.run("find", [f.outDir.absolute, "-type", "f", "-empty", "-delete"]);			// delete empty files
			await runUtil.run("find", [f.outDir.absolute, "-xtype", "l", "-delete"]);					// delete broken symlinks. make sure we do this last just in case a symlink becomes broken because we have deleted the file it points to above
			await runUtil.run("find", [f.outDir.absolute, "-type", "l", "!", "-readable", "-delete"]);	// delete unreadable symlinks, this is a workaround for broken symlinks that point to directories that don't exist and thus don't get caught by the above

			// now find any new files on disk in the output dir that we don't yet know about
			xlog.debug`Program ${fg.orange(this.programid)} locating new files...`;
			const newFilePaths = (await fileUtil.tree(f.outDir.absolute, {nodir : true})).subtractAll([...(f.files.output || []), ...(f.files.prev || []), ...(f.files.new || [])].map(v => v.absolute));

			xlog.debug`Program ${fg.orange(this.programid)} sanity filtering ${newFilePaths.length.toLocaleString()} new files...`;
			let foundDups = false;
			const newDexFiles = (await newFilePaths.parallelMap(async newFilePath =>
			{
				const newFileRel = path.relative(f.outDir.absolute, newFilePath);
				const newFile = await DexFile.create({root : f.root, absolute : newFilePath});

				if(newFile.size>xu.GB && f.input.size<(xu.GB*0.50))
				{
					xlog.warn`Program ${fg.orange(this.programid)} deleting file that is ${newFile.size.bytesToSize()} as it exceeds arbitrary 1GB size sanity check limit from source file that isn't very big: ${fg.green(newFileRel)}`;
					await fileUtil.unlink(newFilePath);
					return;
				}

				// If we are a symlink, we need to make sure we are not pointing outside of our directory or linking to ourself
				if(newFile.isSymlink)
				{
					let linkPath = await Deno.readLink(newFilePath);
					if(!linkPath.startsWith("/"))
						linkPath = path.join(path.dirname(newFilePath), linkPath);

					if(linkPath===newFilePath)
					{
						xlog.warn`Program ${fg.orange(this.programid)} deleting output symlink ${newFileRel} that links to itself`;
						await Deno.remove(newFilePath);		// We have to use Deno.remove() here manually because fileUtil.unlink tries to perform a stat() on it which will fail due to infinite recursion
						return;
					}

					const linkPathRel = path.relative(f.outDir.absolute, linkPath);
					if(linkPathRel.startsWith("../"))
					{
						xlog.warn`Program ${fg.orange(this.programid)} deleting output symlink ${newFileRel} due to linking to a file outside of the output dir: ${linkPath}`;
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
				// we skip for files >25MB unless the program has checkForDups set explicitly
				if((f.input.size<xu.MB*25 || this.checkForDups) && !this.allowDupOut && (this.checkForDups || newFilePaths.length===1) && await fileUtil.areEqual(newFilePath, f.input.absolute))
				{
					xlog.warn`Program ${fg.orange(this.programid)} deleting output file ${newFileRel} due to being identical to input file ${f.input.pretty()}`;
					foundDups = true;
					await fileUtil.unlink(newFilePath);
					return;
				}

				// if the filename >MAX_FILENAME_LENGTH characters we rename it to be <=MAX_FILENAME_LENGTH. This is because later processing adds suffixes such as §.json and thus we need to ensure it's short enough (archive/swf/10003)
				if(newFile.base.length>MAX_FILENAME_LENGTH)
				{
					let newFilename = newFile.base.innerTrim();
					if(newFilename.length>MAX_FILENAME_LENGTH)
						newFilename = newFile.base.innerTruncate(MAX_FILENAME_LENGTH);
					
					xlog.warn`Program ${fg.orange(this.programid)} encountered filename >${MAX_FILENAME_LENGTH} characters [${newFileRel}] rename to [${newFilename}]`;
					await newFile.rename(newFilename, {autoRename : true});
				}

				return newFile;
			})).filter(v => !!v);

			if(foundDups && this.failOnDups)
			{
				xlog.warn`Program ${fg.orange(this.programid)} is aborting due to finding duplicate output files`;
				await newDexFiles.parallelMap(async newDexFile => await fileUtil.unlink(newDexFile.absolute));
				newDexFiles.clear();
			}

			if(newDexFiles.length>0)
			{
				xlog.debug`Adding ${newDexFiles.length.toLocaleString()} new files to file set...`;
				await f.addAll("new", newDexFiles);
			}
		}

		// sort the filenames by depth and then by filename
		if(f.files.new)
		{
			xlog.debug`Program ${fg.orange(this.programid)} located ${f.files.new.length.toLocaleString()} new files...`;
			f.files.new.sortMulti([file => file.rel.split("/").length, file => file.base]);
		}

		if(this.post)
		{
			try { await this.post(r, {xlog}); }
			catch(err) { xlog.error`Program post ${fg.orange(this.programid)} threw error ${err}`; }
		}

		const renameOut = Object.hasOwn(flags, "renameOut") ? flags.renameOut : (typeof this.renameOut==="function" ? await this.renameOut(r) : this.renameOut);

		// if we have some new files, time to rename them
		if(f.outDir && f.files.new?.length===1 && flags.renameKeepFilename)
		{
			// if just 1 file and we were instructed to renameKeepFilename, name the output the same as the input
			await f.files.new[0].rename((originalInput || f.input).base, {replaceExisting : !!isChain});
		}
		else if(f.outDir && f.files.new?.length && renameOut!==false)
		{
			// Otherwise if we renameOut is not false, then proceed with renaming
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
			const restreamerOpts = {r, newName, newExt, suffix, numFiles : f.files.new.length, originalExt, originalInput};

			// See if we have more advanced renaming
			r.renameMap = {};
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
					xlog.info`${fg.pink("Failed")} to pick a renamer for ${f.files.new.length} files, keeping original names`;
				}
				else
				{
					xlog.info`Picked renamer #${renamerNum} for renaming ${f.files.new.length} files...`;

					for(const newFile of f.files.new)
					{
						const replacementName = renamer({fn : newFile.base, ...restreamerOpts}, newFile.base.match(ro.regex)?.groups || {}).join("");
						xlog.info`${fg.orange(this.programid)} renaming output file ${newFile.base} to ${replacementName}`;
						r.renameMap[newFile.base] = replacementName;
						await newFile.rename(replacementName, {replaceExisting : !!isChain});
					}
				}
			}
			else if(f.files.new.length===1)
			{
				const newFilename = newName + suffix + newExt;
				if(newFilename!==f.new.base)
				{
					xlog.info`${fg.orange(this.programid)} renaming single output file ${f.new.base} to ${newFilename}`;
					r.renameMap[f.new.base] = newFilename;
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
			if(this.forbidChildRun)
				r.forbidChildRun = true;
			
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
					// if any program in the chain marked it's state as processed, stop now
					if(r.processed)
						continue;

					const handleNewFiles = async (chainResult, inputFiles, chainProgramid) =>
					{
						if(!chainResult?.f?.new)
						{
							if(chainResult.processed)
								r.processed = true;
							else
								xlog.warn`Chain ${progRaw} did ${fg.red("NOT")} produce any new files!`;
								
							if(!xlog.atLeast("trace"))
							{
								await chainResult.unlinkHomeOut();
								
								if(!this.chainFailKeep || !(await this.chainFailKeep(r, inputFiles, chainResult, chainProgramid)))
								{
									xlog.info`Deleting ${inputFiles.length} chain input files!`;
									for(const inputFile of inputFiles)
										await f.remove("new", inputFile, {unlink : true});
								}
							}
							return;
						}

						// copy our new chain output files over to the dir the input files are in. WARNING! This doesn't do ANY collision avoidance at all, so if there are duplicate filenames, they will overwrite the existing files
						xlog.debug`Handling ${chainResult.f.all.length} chain file results...`;

						const targetChainDirPath = inputFiles[0].dir.startsWith(f.outDir.absolute) ? inputFiles[0].dir : f.outDir.absolute;
						let newFileSet=null;

						if(chainResult.flags.bulkCopyOut)
						{
							await runUtil.run("rsync", ["-sa", `${chainResult.f.outDir.absolute}/`, targetChainDirPath]);
							newFileSet = await FileSet.create(f.root);
							await chainResult.f.files.new.parallelMap(async file => await newFileSet.add("new", path.join(targetChainDirPath, path.relative(chainResult.f.outDir.absolute, file.absolute))));
						}
						else
						{
							newFileSet = await chainResult.f.rsyncTo(targetChainDirPath, {type : "new", relativeFrom : chainResult.f.outDir.absolute});
						}

						newFileSet.changeRoot(f.root);
						await f.addAll("new", newFileSet.files.new);

						// remove any old input files that are not part of our new chain output/new files
						for(const inputFile of inputFiles)
						{
							if(!newFileSet.files.new.some(v => v.absolute===inputFile.absolute))
								await f.remove("new", inputFile, {unlink : true});
						}
						
						xlog.info`Chain ${progRaw} resulted in ${newFileSet.files.new.length.toLocaleString()} new files: ${newFileSet.files.new.map(v => v.rel).join(" ").innerTruncate(300)}`;

						await chainResult.unlinkHomeOut();
					};
					
					const baseChainProgOpts = {isChain : true, format, xlog, chainParent : r};
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
							await handleNewFiles(await Program.runProgram(progRaw.startsWith("?") ? progRaw.substring(1) : progRaw, newFile, chainProgOpts), [newFile], chainProgramid);
						}, await sysUtil.optimalParallelism(newFiles.length));
					}
				}

				if(this.chainPost)
				{
					try { await this.chainPost(r); }
					catch(err) { xlog.error`Program chainPost ${fg.orange(this.programid)} threw error ${err}`; }
				}
			}
		}
		else
		{
			xlog.debug`No new files detected from ${r.programid}`;
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
			progRaw = chainParts[0].trim();
		}

		const {programid, flags, progOptions : moreProgOptions} = Program.parseProgram(progRaw);
		if(RUNTIME.forbidProgram.has(programid))
			return RunState.create({programid, xlog, f : fRaw instanceof FileSet ? fRaw : await FileSet.create(fRaw instanceof DexFile ? fRaw.root : path.dirname(fRaw), "input", fRaw)});
			
		Object.assign(progOptions, moreProgOptions);

		// run prog
		progOptions.flags ||= {};
		Object.assign(progOptions.flags, flags);

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
			
			const outDirPath = await fileUtil.genTempPath(undefined, "", {maxFilenameLength : 8});	// an empty suffix ensures no .tmp default suffix and won't generate a path > 8 chars which would be a problem for DOS
			await Deno.mkdir(outDirPath, {recursive : true});
			await f.add("outDir", outDirPath);

			const homeDirPath = await fileUtil.genTempPath(undefined, `${programid}_home`);
			await Deno.mkdir(homeDirPath, {recursive : true});
			await f.add("homeDir", homeDirPath);
		}

		let originalOutDir = null;
		if(flags.subOutDir)
		{
			originalOutDir = f.outDir.absolute;

			const subOutDirPath = path.join(f.outDir.absolute, flags.subOutDir);
			await Deno.mkdir(subOutDirPath, {recursive : true});
			await f.removeType("outDir");
			await f.add("outDir", subOutDirPath);
		}

		if(progOptions.outFile)
			await f.add("outFile", progOptions.outFile);

		const debugPart = Object.assign({}, progOptions);
		delete debugPart.xlog;
		xlog.trace`Program ${progRaw} converted to ${debugPart} with f ${f}`;
		
		// if we are instructed to not include aux files, rsync them somewhere else and delete the originals, then we resync right after back
		let tmpAuxDir = null;
		let noAuxFiles = [];
		if(flags.noAux && f.files?.aux?.length)
		{
			tmpAuxDir = await fileUtil.genTempPath(undefined, "noAux");
			await Deno.mkdir(tmpAuxDir);
			noAuxFiles = f.files.aux;
			delete f.files.aux;
			await noAuxFiles.parallelMap(async file => await fileUtil.move(file.absolute, path.join(tmpAuxDir, file.base)));
		}

		const programResult = await program.run(f, progOptions);

		if(tmpAuxDir && noAuxFiles)
		{
			await noAuxFiles.parallelMap(async file => await fileUtil.move(path.join(tmpAuxDir, file.base), file.absolute));
			f.files.aux = noAuxFiles;
			await fileUtil.unlink(tmpAuxDir, {recursive : true});
		}

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
		
		if(originalOutDir)
		{
			await f.removeType("outDir");
			await f.add("outDir", originalOutDir);
		}

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

	static hasProgram(progRaw)
	{
		const {programid} = Program.parseProgram(progRaw);
		return Object.hasOwn(programs, programid);
	}

	// forms a path to dexvert/bin/{rel}
	static binPath(rel)
	{
		return path.join(import.meta.dirname, "..", "bin", rel);
	}

	// returns args needed to call a sub deno script
	static denoArgs(...args)
	{
		return runUtil.denoArgs(...args);
	}

	// returns env needed to properly run deno scripts
	static denoEnv()
	{
		return runUtil.denoEnv();
	}

	// returns env needed to properly run amiga programs under vamos
	static vamosArgs(bin)
	{
		return ["-c", "/mnt/compendium/DevLab/dexvert/amiga/.vamosrc", "--", path.join("/mnt/compendium/DevLab/dexvert/amiga/System/C", bin)];
	}
}
