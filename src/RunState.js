import {xu} from "xu";
import {validateClass} from "./validate.js";
import {FileSet} from "./FileSet.js";

export class RunState
{
	meta = {};
	baseKeys = Object.keys(this);
	
	// builder to get around the fact that constructors can't be async
	static create(o)
	{
		const runState = new this();
		Object.assign(runState, o);
		validateClass(runState, {
			// required
			programid : {type : "string", required : true},
			input     : {type : FileSet, required : true},
			output    : {type : FileSet}
		});
		return runState;
	}

	serialize()
	{
		const o = {};
		o.programid = this.programid;
		o.input = this.input.serialize();
		if(this.output)
			o.output = this.output.serialize();
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
		r.push(`${prefix}${xu.cf.fg.white("Program")} ${xu.cf.fg.orange(this.programid)}${this.status ? ` ${xu.cf.fg.cyan("—")} ${xu.cf.fg.white("Status:")} ${xu.inspect(this.status)}` : ""}`);
		if(this.bin)
			r.push(`\n${prefix}\t${xu.cf.fg.white("ran:")} ${xu.cf.fg.peach(this.bin)} ${(this.args || []).map(arg => (arg.includes(" ") ? `${xu.cf.fg.cyan('"')}${xu.cf.fg.green(arg)}${xu.cf.fg.cyan('"')}` : xu.cf.fg.green(arg))).join(" ")} with options ${xu.inspect(this.runOptions || {})}`);	// eslint-disable-line max-len
		r.push(`\n${prefix}\t${xu.cf.fg.white("meta:")} ${xu.inspect(this.meta).squeeze()}`);
		if(Object.hasOwn(this, "stdout"))
		{
			r.push(`\n${prefix}\t${xu.cf.fg.white("stdout (squeezed):")} ${this.stdout.squeeze()}`);
			r.push(`\n${prefix}\t${xu.cf.fg.white("stderr (squeezed):")} ${this.stderr.squeeze()}`);
		}
		return r.join("");
	}
}
