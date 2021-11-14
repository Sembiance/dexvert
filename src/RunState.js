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

	pretty(prefix="")
	{
		const r = [];
		r.push(`${prefix}${fg.white("Program")} ${fg.orange(this.programid)}${this.status ? ` ${fg.cyan("—")} ${fg.white("Status:")} ${xu.inspect(this.status)}` : ""}`);
		if(this.bin)
			r.push(`\n${prefix}\t${fg.white("   ran:")} ${fg.peach(this.bin)} ${(this.args || []).map(arg => (arg.includes(" ") ? `${fg.cyan('"')}${fg.green(arg)}${fg.cyan('"')}` : fg.green(arg))).join(" ")} with options ${xu.inspect(this.runOptions || {}).squeeze()}`);
		r.push(`\n${prefix}\t${fg.white("  meta:")} ${xu.inspect(this.meta).squeeze()}`);
		if(Object.hasOwn(this, "stdout"))
		{
			r.push(`\n${prefix}\t${fg.white("stdout:")} ${this.stdout.squeeze()}`);
			r.push(`\n${prefix}\t${fg.white("stderr:")} ${this.stderr.squeeze()}`);
		}
		return r.join("");
	}
}
