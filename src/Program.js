import {xu} from "xu";
import {fileUtil, runUtil} from "xutil";
import * as path from "https://deno.land/std@0.111.0/path/mod.ts";
import { assertStrictEquals } from "https://deno.land/std@0.110.0/testing/asserts.ts";
import {validateClass} from "./validate.js";
import {RunState} from "./RunState.js";

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
			loc       : {type : "string", required : true, enum : ["local", "amigappc", "gentoo", "win2k", "winxp"]},	// where to run this program at. Default is local

			// meta
			gentooPackage  : {types : ["string", Array]},	// gentoo package atom
			gentooOverlay  : {type : "string"},				// gentoo overlay
			gentooUseFlags : {type : "string"},				// gentoo use flags set for the gentoo package
			website        : {type : "string", url : true},	// homepage URL for this program
			notes          : {type : "string"},				// notes about this program

			// execution
			bin  : {type : "string"},				// path to the binary to run. Can't have bin and exec.
			exec : {type : "function", length : 1},	// function of code to run instead of bin. Can't have bin and exec.
			args : {type : "function", length : 1}, // returns an array of the program arguments
			post : {type : "function", length : 1}	// is called after the program is finished being executed
		});

		return program;
	}

	// runs the current program with the given input and output FileSets and various options
	async run(input, output, {timeout=DEFAULT_TIMEOUT, verbose=0}={})
	{
		const r = RunState.create({programid : this.programid, input, output});
		if(this.bin)
		{
			r.bin = this.bin;
			r.args = await this.args(r);
			r.runOptions = {cwd : input.root, timeout};
			if(verbose>=4)
				xu.log`Program ${xu.cf.fg.orange(this.programid)} running as \`${this.bin} ${r.args.map(arg => (arg.includes(" ") ? `"${arg}"` : arg)).join(" ")}\` with options ${r.runOptions}`;
			const {stdout, stderr, status} = await runUtil.run(this.bin, r.args, r.runOptions);
			Object.assign(r, {stdout, stderr, status});
		}
		else if(this.exec)
		{
			if(verbose>=4)
				xu.log`Program ${xu.cf.fg.orange(this.programid)} executing ${".exec"} steps`;
			await this.exec(r);
		}

		if(this.post)
			await this.post(r);

		if(verbose>=3)
			console.log(r.pretty());

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
			// TODO REMOVE BELOW AFTER CONVERTING ALL PROGRAMS
			if(!(await fileUtil.readFile(programFilePath)).includes(" extends Program"))
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
