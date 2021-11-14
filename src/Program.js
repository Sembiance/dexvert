import {xu, fg} from "xu";
import {fileUtil, runUtil} from "xutil";
import * as path from "https://deno.land/std@0.111.0/path/mod.ts";
import { assertStrictEquals } from "https://deno.land/std@0.110.0/testing/asserts.ts";
import {validateClass, validateObject} from "./validate.js";
import {RunState} from "./RunState.js";
import {FileSet} from "./FileSet.js";
import {DexFile} from "./DexFile.js";

const DEFAULT_TIMEOUT = xu.MINUTE*2;

export class Program
{
	static programs = null;
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
			loc       : {type : "string", required : true, enum : ["local", "amigappc", "gentoo", "win2k", "winxp"]},

			// meta
			gentooPackage  : {types : ["string", Array]},
			gentooOverlay  : {type : "string"},
			gentooUseFlags : {type : "string"},
			website        : {type : "string", url : true},
			notes          : {type : "string"},
			unsafe         : {type : "boolean"},
			flags          : {type : Object},
			renameOut      : {type : Object},
			runOptions     : {type : Object},

			// execution
			bin    : {type : "string"},
			outExt : {type : "function", length : [0, 1]},
			exec   : {type : "function", length : 1},
			args   : {type : "function", length : 1},
			pre    : {type : "function", length : 1},
			post   : {type : "function", length : 1}
		});

		if(program.renameOut)
			validateObject(program.renameOut, {ext : {type : "string"}, name : {type : "boolean"}});

		return program;
	}

	// runs the current program with the given input and output FileSets and various options
	async run(f, {timeout=DEFAULT_TIMEOUT, verbose=0, flags={}, originalInput}={})
	{
		if(!(f instanceof FileSet))
			throw new Error(`Program ${fg.orange(this.programid)} run didn't get a FileSet as arg 1`);
		
		const unknownFlags = Object.keys(flags).subtractAll(Object.keys(this.flags || {}));
		if(unknownFlags.length>0)
			throw new Error(`Program ${fg.orange(this.programid)} run got unknown flags: ${unknownFlags.join(" ")}`);

		// create a RunState to store program results/meta
		const r = RunState.create({programid : this.programid, f, flags});

		if(this.pre)
			await this.pre(r);

		if(this.bin)
		{
			// run a program on disk
			r.bin = this.bin;
			r.args = await this.args(r);
			r.runOptions = {cwd : f.root, timeout};
			if(f.homeDir)
				r.runOptions.env = {HOME : f.homeDir.absolute};
			if(verbose>=5)
				r.runOptions.verbose = true;
			if(this.runOptions)
				Object.assign(r.runOptions, this.runOptions);
				
			if(verbose>=4)
				xu.log`Program ${fg.orange(this.programid)} running as \`${this.bin} ${r.args.map(arg => (arg.includes(" ") ? `"${arg}"` : arg)).join(" ")}\` with options ${r.runOptions}`;
			const {stdout, stderr, status} = await runUtil.run(this.bin, r.args, r.runOptions);
			Object.assign(r, {stdout, stderr, status});
		}
		else if(this.exec)
		{
			// run arbitrary javascript code
			if(verbose>=4)
				xu.log`Program ${fg.orange(this.programid)} executing ${".exec"} steps`;
			await this.exec(r);
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
			for(const newFilePath of (await fileUtil.tree(f.outDir.absolute, {nodir : true})).subtractAll((f.output || []).map(v => v.absolute)))
			{
				// if the new file is identical to our input file, delete it
				if(await fileUtil.areEqual(newFilePath, f.input.absolute))
				{
					if(verbose>=3)
						xu.log`Program ${fg.orange(this.programid)} deleting output file ${newFilePath} due to being identical to input file ${f.input.pretty()}`;
					await Deno.remove(newFilePath);
					continue;
				}

				// add our new file to our fileset
				await f.add("new", newFilePath);
			}
		}

		if(this.post)
			await this.post(r);
		
		// if we have just a single new output file, we perform some renaming of it
		if(f.outDir && f.files.new?.length===1)
		{
			const ro = Object.assign({ext : this.outExt ? this.outExt(r) || "" : "", name : true}, this.renameOut);
			const newFilename = (ro.name===true ? (originalInput?.name || f.input.name) : (ro.name || f.new.name)) + (ro.ext || f.new.ext);
			if(newFilename!==f.new.base)
			{
				if(verbose>=3)
					xu.log`Program ${fg.orange(this.programid)} renaming the single output file [${f.new.pretty()}] to ${newFilename}`;
				await f.new.rename(newFilename);
			}
		}

		if(verbose>=3)
			console.log(r.pretty());

		return r;
	}

	// runs the programid program
	static async runProgram(programid, ...args)
	{
		const program = (await this.loadPrograms())[programid];
		if(!program)
			throw new Error(`Unknown programid: ${programid}`);

		// if our first arg isn't a FileSet, then we will create a temporary one
		if(!(args[0] instanceof FileSet))
		{
			const arg0 = args.shift();
			const inputFile = arg0 instanceof DexFile ? arg0.clone() : await DexFile.create(arg0);
			const f = await FileSet.create(inputFile.root, "input", inputFile);
			
			const outDirPath = await fileUtil.genTempPath(undefined, `${programid}-out`);
			await Deno.mkdir(outDirPath, {recursive : true});
			await f.add("outDir", outDirPath);

			const homeDirPath = await fileUtil.genTempPath(undefined, `${programid}-home`);
			await Deno.mkdir(homeDirPath, {recursive : true});
			await f.add("homeDir", homeDirPath);

			args.unshift(f);
		}
		
		return program.run(...args);
	}

	// forms a path to dexvert/bin/{subPath}
	static binPath(subPath)
	{
		return path.join(xu.dirname(import.meta), "..", "bin", subPath);
	}

	// loads all src/program/*/*.js files from disk as Program objects. These are cached in the static this.programs cache
	static async loadPrograms()
	{
		if(this.programs!==null)
		{
			await xu.waitUntil(() => Object.isObject(this.programs));
			return this.programs;
		}
		
		this.programs = false;
		const programs = {};

		for(const programFilePath of await fileUtil.tree(path.join(xu.dirname(import.meta), "program"), {nodir : true, regex : /[^/]+\/.+\.js$/}))
		{
			// TODO REMOVE BELOW AFTER CONVERTING ALL PROGRAMS
			if(!(await fileUtil.readFile(programFilePath)).includes(" extends Program") || (await fileUtil.readFile(programFilePath)).startsWith("/*"))
				continue;
			// TODO REMOVE ABOVE AFTER CONVERTING ALL PROGRAMS

			const progamModule = await import(programFilePath);
			const programid = Object.keys(progamModule)[0];

			// class name must match filename
			assertStrictEquals(programid, path.basename(programFilePath, ".js"), `program file [${programFilePath}] does not have a matching class name [${programid}]`);

			// check for duplicates
			if(programs[programid])
				throw new Error(`program [${programid}] at ${programFilePath} is a duplicate of ${programs[programid]}`);

			// create the class and validate it
			programs[programid] = progamModule[programid].create();
			if(!(programs[programid] instanceof this))
				throw new Error(`program [${programid}] at [${programFilePath}] is not of type Program`);
		}
		
		this.programs = programs;
		return this.programs;
	}
}
