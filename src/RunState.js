import {xu, fg} from "xu";
import {validateClass} from "./validate.js";
import {FileSet} from "./FileSet.js";
import {fileUtil} from "xutil";
import {path} from "std";

export class RunState
{
	meta = {};
	flags = {};
	baseKeys = Object.keys(this);
	
	// builder to get around the fact that constructors can't be async
	static create(o)
	{
		const runState = new this();
		Object.assign(runState, o);
		validateClass(runState, {
			// required
			programid : {type : "string", required : true},
			f         : {type : FileSet, required : true},
			flags     : {type : Object}
		});
		return runState;
	}

	// returns f.input.rel
	inFile({backslash, absolute}={})
	{
		const result = absolute ? this.f.input.absolute : path.relative(this.cwd, this.f.input.absolute);
		return backslash ? result.replaceAll("/", "\\") : result;
	}

	inFiles({backslash, absolute}={})
	{
		return this.f.files.input.map(input =>
		{
			const result = absolute ? input.absolute : path.relative(this.cwd, input.absolute);
			return backslash ? result.replaceAll("/", "\\") : result;
		}).sortMulti();
	}

	// will return f.outFile if set, otherwise will return <f.outDir>/<filename> if it doesn't exist, otherwise it will return a non-existing filename in <f.outDir>/<random><filename>
	async outFile(filename="outfile", {backslash, absolute}={})
	{
		let result = null;
		if(this.f.outFile)
		{
			result = absolute ? this.f.outFile.absolute : path.relative(this.cwd, this.f.outFile.absolute);
		}
		else
		{
			const newFilePath = path.join(this.f.outDir.absolute, filename);
			result = (await fileUtil.exists(newFilePath) ? await fileUtil.genTempPath(this.f.outDir.absolute, filename) : newFilePath);
			if(!absolute)
				result = path.relative(this.cwd, result);
		}

		return backslash ? result.replaceAll("/", "\\") : result;
	}

	// returns r.f.outDir.rel
	outDir({absolute}={})
	{
		return absolute ? this.f.outDir.absolute : path.relative(this.cwd, this.f.outDir.absolute);
	}

	serialize()
	{
		const o = {};
		o.programid = this.programid;
		o.f = this.f.serialize();
		o.meta = xu.parseJSON(JSON.stringify(o.meta));	// Can include classes and other non-JSON friendly things
		for(const key of ["bin", "args", "runOptions", "cwd", "dosData", "qemuData"])
		{
			if(Object.hasOwn(this, key))
				o[key] = this[key];
		}

		return o;
	}

	pretty(pre="")
	{
		const r = [];
		r.push(`${pre}${xu.paren(fg.orange(this.programid))}`);
		if(this.bin)
		{
			r.push(` ${fg.peach(this.bin)} ${(this.args || []).map(arg => (!arg.includes(" ") ? xu.quote(fg.green(arg)) : fg.green(arg))).join(" ")}`);
			if(this.status)
				r.push(` ${xu.paren(xu.inspect(this.status))}`);
			if(xu.verbose>=4)
			{
				r.push(`\n${pre}\t${xu.colon("   cwd")}${this.cwd}`);
				r.push(`\n${pre}\t${xu.colon("  opts")}${xu.inspect(this.runOptions || {}).squeeze()}`);
			}
		}
		else if(this.qemuData)
		{
			r.push(` QEMU ${fg.cyan(this.qemuData.osid)} ${fg.peach(this.qemuData.cmd)} ${(this.qemuData.args || []).map(arg => (!arg.includes(" ") ? xu.quote(fg.green(arg)) : fg.green(arg))).join(" ")}`);
			if(this.status)
				r.push(` ${xu.paren(xu.inspect(this.status))}`);
		}
		else if(this.dosData)
		{
			r.push(` DOS ${fg.peach(this.dosData.cmd)} ${(this.dosData.args || []).map(arg => (!arg.includes(" ") ? xu.quote(fg.green(arg)) : fg.green(arg))).join(" ")}`);
			if(this.status)
				r.push(` ${xu.paren(xu.inspect(this.status))}`);
		}
		
		if(xu.verbose>=3 && Object.keys(this.meta || {}).length>0)
			r.push(`\n${pre}\t${xu.colon("  meta")}${xu.inspect(this.meta).squeeze()}`);

		if(xu.verbose>=5 || (xu.verbose>=4 && (this.stdout || "").trim().length>0))
			r.push(`\n${pre}\t${xu.colon("stdout")}${(this.stdout || "").squeeze()}`);
		if(xu.verbose>=5 || (xu.verbose>=4 && (this.stderr || "").trim().length>0))
			r.push(`\n${pre}\t${xu.colon("stderr")}${(this.stderr || "").squeeze()}`);
			
		return r.join("");
	}
}
