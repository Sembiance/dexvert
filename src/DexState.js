import {xu, fg} from "xu";
import {printUtil} from "xutil";
import {validateClass, validateObject} from "./validate.js";
import {FileSet} from "./FileSet.js";
import {DexFile} from "./DexFile.js";
import {Format} from "./Format.js";
import {Identification} from "./Identification.js";

export class DexPhase
{
	meta = {};
	ran = [];
	baseKeys = Object.keys(this);

	// builder to get around the fact that constructors can't be async
	static create(o)
	{
		const dexPhase = new this();
		Object.assign(dexPhase, o);

		validateClass(dexPhase, {
			// required
			input  : {type : FileSet, required : true},
			output : {type : FileSet, required : true},
			format : {type : Format, required : true},
			id     : {type : Identification, required : true}
		});
		
		return dexPhase;
	}

	serialize()
	{
		const o = {};
		for(const key of ["input", "output", "format", "id"])
			o[key] = this[key].serialize();
		o.meta = xu.parseJSON(JSON.stringify(this.meta));
		o.ran = this.ran.map(v => v.serialize());
		return o;
	}

	pretty(prefix="")
	{
		const r = [];
		r.push(`${prefix}${fg.white(" input:")} ${this.input.pretty(`${prefix}\t`).trim()}`);
		r.push(`\n${prefix}${fg.white("output:")} ${this.output.pretty(`${prefix}\t`).trim()}`);
		r.push(`\n${prefix}${fg.white("  meta:")} ${xu.inspect(this.meta).squeeze()}`);
		r.push(`\n${prefix}${fg.white("format:")} ${this.format.pretty(`${prefix}\t`).trim()}`);
		r.push(`\n${prefix}${fg.white("    id:")} ${this.id.pretty(`${prefix}\t`).trim()}`);
		r.push(`\n${prefix}${fg.white("   ran:")} ${fg.yellowDim(this.ran.length)} programs`);
		if(this.ran.length>0)
			r.push(this.ran.map(v => v.pretty(`${prefix}\t`).join("")));
		return r.join("");
	}
}

export class DexState
{
	phase = null;
	past = [];
	baseKeys = Object.keys(this);

	// builder to get around the fact that constructors can't be async
	static create(o)
	{
		const dexState = new this();
		Object.assign(dexState, o);

		validateClass(dexState, {
			// required
			original : {type : Object, required : true},

			// optional
			verbose : {type : "number", range : [0, 6]}
		});

		validateObject(dexState.original, {
			input  : {type : DexFile, required : true},
			output : {type : DexFile, required : true}
		});

		return dexState;
	}

	// starts the next phase
	startPhase(o)
	{
		const dexPhase = o instanceof DexPhase ? o : DexPhase.create(o);
		if(this.phase)
			this.past.push(this.phase);
		this.phase = dexPhase;
		return dexPhase;
	}

	// convenience methods to access current phase properties
	get input() { return this.phase.input; }
	get output() { return this.phase.output; }
	get format() { return this.phase.format; }
	get meta() { return this.phase.meta; }
	get id() { return this.phase.id; }

	serialize()
	{
		const o = {};
		o.original = Object.fromEntries(Object.entries(this.original).map(([k, v]) => ([k, v.serialize()])));
		if(this.phase)
			o.phase = this.phase.serialize();
		o.past = this.past.map(v => v.serialize());
		return o;
	}

	// returns a pretty string for this DexState, useful for debugging purposes
	pretty(prefix="")
	{
		const r = [];
		r.push(printUtil.majorHeader("DexState"));
		r.push(`${prefix}${fg.white("         result:")} ${this.processed ? fg.cyan("PROCESSED") : fg.peach("NOT PROCESSED")} ${this.format.untouched ? fg.deepSkyblue("**UNTOUCHED**") : ""}`);
		r.push(`\n${prefix}${fg.white(" original input:")} ${this.original.input.pretty()}`);
		r.push(`\n${prefix}${fg.white("original output:")} ${this.original.output.pretty()}`);
		r.push(`\n${prefix}${fg.white("  CURRENT PHASE:")}\n${this.phase.pretty(`${prefix}\t`)}`);
		r.push(`\n${prefix}${fg.brown("    PAST PHASES:")} ${fg.yellow(this.past.length)} phases\n${this.past.map(pastPhase => pastPhase.pretty(`${prefix}\t`)).join("\n")}`);
		return r.join("");
	}
}
