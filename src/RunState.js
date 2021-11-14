import {xu, fg} from "xu";
import {validateClass} from "./validate.js";
import {FileSet} from "./FileSet.js";

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
		if(xu.verbose>=2 && Object.keys(this.meta || {}).length>0)
			r.push(`\n${pre}\t${xu.colon("  meta")}${xu.inspect(this.meta).squeeze()}`);

		if(xu.verbose>=3 && (this.stdout || "").trim().length>0)
			r.push(`\n${pre}\t${xu.colon("stdout")}${this.stdout.squeeze()}`);
		if(xu.verbose>=3 && (this.stderr || "").trim().length>0)
			r.push(`\n${pre}\t${xu.colon("stderr")}${this.stderr.squeeze()}`);
			
		return r.join("");
	}
}
