import {xu, fg} from "xu";
import {validateClass} from "validator";
import {FileSet} from "./FileSet.js";
import {fileUtil, printUtil} from "xutil";
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
			xlog      : {required : true},
			flags     : {type : Object}
		});
		return runState;
	}

	// returns f.input.rel
	inFile({backslash, absolute}={})
	{
		const result = absolute ? (this.mirrorInToCWD ? path.join(this.cwd, this.f.input.base) : this.f.input.absolute) : (this.mirrorInToCWD ? this.f.input.base : path.relative(this.cwd, this.f.input.absolute));
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
	outDir({absolute, trailingSlash}={})
	{
		let result = absolute ? this.f.outDir.absolute : path.relative(this.cwd, this.f.outDir.absolute);
		
		if(trailingSlash)
			result = path.join(result, "/");

		return result;
	}

	// Removes from disk the outDir and homeDir of this RunState, used to cleanup temporary excess files from temporary program runs
	async unlinkHomeOut()
	{
		if(!this.xlog.atLeast("trace"))
		{
			await fileUtil.unlink(this.f.outDir.absolute, {recursive : true});
			await fileUtil.unlink(this.f.homeDir.absolute, {recursive : true});
		}
	}

	serialize()
	{
		const o = {};
		o.programid = this.programid;
		//o.f = this.f.serialize();	// Not included for brevity
		o.meta = xu.parseJSON(JSON.stringify(o.meta), {});	// Can include classes and other non-JSON friendly things
		for(const key of ["args", "bin", "cwd", "dosData", "forbidChildRun", "osData"])
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
				r.push(` ${xu.paren(printUtil.inspect(this.status))}`);
			
			if(this.xlog.atLeast("debug"))
			{
				r.push(`\n${pre}\t${xu.colon("   cwd")}${this.cwd}`);
				r.push(`\n${pre}\t${xu.colon("  opts")}${printUtil.inspect(this.runOptions || {}).squeeze()}`);
				r.push(`\n${pre}\t${xu.colon(" flags")}${printUtil.inspect(this.flags || {}).squeeze()}`);
			}
		}
		else if(this.osData)
		{
			r.push(`   OS ${fg.cyan(this.osData.osid)} ${fg.peach(this.osData.cmd)} ${(this.osData.args || []).map(arg => (!arg.includes(" ") ? xu.quote(fg.green(arg)) : fg.green(arg))).join(" ")}`);
			if(this.status)
				r.push(` ${xu.paren(printUtil.inspect(this.status))}`);
		}
		else if(this.dosData)
		{
			r.push(` DOS ${fg.peach(this.dosData.cmd)} ${(this.dosData.args || []).map(arg => (!arg.includes(" ") ? xu.quote(fg.green(arg)) : fg.green(arg))).join(" ")}`);
			if(this.status)
				r.push(` ${xu.paren(printUtil.inspect(this.status))}`);
		}
		
		if(this.xlog.atLeast("info") && Object.keys(this.meta || {}).length>0)
			r.push(`\n${pre}\t${xu.colon("  meta")}${printUtil.inspect(this.meta).squeeze()}`);

		if(this.xlog.atLeast("trace") || (this.xlog.atLeast("debug") && (this.stdout || "").trim().length>0))
			r.push(`\n${pre}\t${xu.colon("stdout")}${(this.stdout || "")[this.xlog.atLeast("trace") ? "toString" : "squeeze"]().innerTruncate(this.xlog.atLeast("debug") ? Number.MAX_SAFE_INTEGER : 200)}`);
		if(this.xlog.atLeast("trace") || (this.xlog.atLeast("debug") && (this.stderr || "").trim().length>0))
			r.push(`\n${pre}\t${xu.colon("stderr")}${(this.stderr || "")[this.xlog.atLeast("trace") ? "toString" : "squeeze"]().innerTruncate(this.xlog.atLeast("debug") ? Number.MAX_SAFE_INTEGER : 200)}`);
			
		return r.join("");
	}
}
