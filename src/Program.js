import {xu} from "xu";
import {fileUtil, runUtil} from "xutil";
import * as path from "https://deno.land/std@0.111.0/path/mod.ts";
import { assertStrictEquals } from "https://deno.land/std@0.110.0/testing/asserts.ts";
import {validateClass} from "./validate.js";
import {RunState} from "./RunState.js";
import {FileSet} from "./FileSet.js";

const DEFAULT_TIMEOUT = xu.MINUTE*2;
const DEFAULT_QUOTA_DISK = xu.GB*10;

export class Program
{
	static programs = null;
	programid = this.constructor.name;
	loc = "local";
	baseKeys = Object.keys(this);

	// builder to get around the fact that constructors can't be async
	constructor({allowNew}) { if(!allowNew) { throw new Error(`Use static ${this.constructor.name}.create() instead`); } }	// eslint-disable-line curly
	static create()
	{
		const program = new this({allowNew : true});

		if(Object.hasOwn(program, "bin") && Object.hasOwn(program, "exec"))
			throw new Error(`class [${this.constructor.name}] can't have both [bin] and [exec] properties.`);

		validateClass(program, {
			// required
			programid : {type : "string", required : true},	// automatically set to the constructor name
			loc       : {type : "string", required : true, enum : ["gentoo", "local", "amigappc", "win2k", "winxp"]},	// where to run this program at. Default is gentoo

			// meta
			gentooPackage  : {type : "string"},				// gentoo package atom
			gentooUseFlags : {type : "string"},				// gentoo use flags set for the gentoo package
			gentooOverlay  : {type : "string"},				// gentoo overlay
			website        : {type : "string", url : true}, 	// homepage URL for this program

			// execution
			bin  : {type : "string"},				// path to the binary to run. Can't have bin and exec.
			exec : {type : "function", length : 1},	// function of code to run instead of bin. Can't have bin and exec.
			args : {type : "function", length : 1}, // returns an array of the program arguments
			post : {type : "function", length : 1}	// is called after the program is finished being executed
		});

		return program;
	}

	// runs the current program with the given input and output FileSets and various options
	async run(_input, _output, {diskQuota=DEFAULT_QUOTA_DISK, timeout=DEFAULT_TIMEOUT, verbose=false}={})
	{
		// ensure input and output are FileSets
		const input = _input instanceof FileSet ? _input : await FileSet.create(_input);
		const output = _output instanceof FileSet ? _output : await FileSet.create(_output);

		// all files processed are on a RAM mounted temp directory with a disk limit
		const ramDirPath = await fileUtil.genTempPath(undefined, `${this.programid}`);
		await Deno.mkdir(ramDirPath);
		await runUtil.run("sudo", ["mount", "-t", "tmpfs", "-o", `size=${diskQuota},mode=0777,nodev,noatime`, "tmpfs", ramDirPath]);

		// we rsync them instead of symlink in order to prevent problems with some programs not working with symlinks correctly or modifying the original (bad program), wanting exclusive locks (even a thing under linux?), etc
		const r = RunState.create({inputOriginal : input, input : await input.rsyncTo(ramDirPath), output});
		if(this.bin)
		{
			const args = await this.args(r);
			const runOptions = {cwd : ramDirPath, timeout, verbose};
			if(verbose)
				console.log(`Program ${this.programid} running as [${this.bin} ${args.map(arg => (arg.includes(" ") ? `"${arg}"` : arg)).join(" ")}] with options ${runOptions}`);
			const {stdout, stderr, status} = await runUtil.run(this.bin, args, runOptions);
			Object.assign(r, {stdout, stderr, status});
		}
		else if(this.exec)
		{
			if(verbose)
				console.log(`Program ${this.programid} executing .exec steps`);
			await this.exec(r);
		}

		if(this.post)
			await this.post(r);

		await runUtil.run("sudo", ["umount", ramDirPath]);
		await Deno.remove(ramDirPath);

		return r;
	}

	// runs the programid program
	static async runProgram(programid, ...args)
	{
		const program = (await this.loadPrograms())[programid];
		if(!program)
			return null;
		
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
