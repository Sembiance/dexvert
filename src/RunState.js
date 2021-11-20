import {xu, fg} from "xu";
import {validateClass} from "./validate.js";
import {FileSet} from "./FileSet.js";
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
		const result = this.f.input[absolute ? "absolute" : "rel"];
		return backslash ? result.replaceAll("/", "\\") : result;
	}

	// will return f.outFile.rel if set, otherwise will return <f.outDir.rel>/<filename>
	outFile(filename="outfile", {backslash, absolute}={})
	{
		const result = this.f.outFile ? this.f.outFile[absolute ? "absolute" : "rel"] : path.join(this.f.outDir[absolute ? "absolute" : "rel"], filename);
		return backslash ? result.replaceAll("/", "\\") : result;
	}

	// returns r.f.outDir.rel
	outDir({absolute}={})
	{
		return absolute ? this.f.outDir.absolute : this.f.outDir.rel;
	}

	serialize()
	{
		const o = {};
		o.programid = this.programid;
		o.f = this.f.serialize();
		o.meta = xu.parseJSON(JSON.stringify(o.meta));	// Can include classes and other non-JSON friendly things
		for(const key of ["bin", "args", "runOptions"])
		{
			if(Object.hasOwn(this, key))
				o[key] = this[key];
		}
		// TODO Maybe add dosData/qemuData ?
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
				r.push(`\n${pre}\t${xu.colon("  opts")}${xu.inspect(this.runOptions || {}).squeeze()}`);
		}
		else if(this.qemuData)
		{
			r.push(` QEMU ${fg.cyan(this.qemuData.osid)} ${fg.peach(this.qemuData.cmd)} ${(this.qemuData.args || []).map(arg => (!arg.includes(" ") ? xu.quote(fg.green(arg)) : fg.green(arg))).join(" ")}`);
			if(this.status)
				r.push(` ${xu.paren(xu.inspect(this.status))}`);
		}
		else if(this.dosData)
		{
			r.push(` DOS ${fg.peach(this.qemuData.cmd)} ${(this.qemuData.args || []).map(arg => (!arg.includes(" ") ? xu.quote(fg.green(arg)) : fg.green(arg))).join(" ")}`);
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
