import {xu} from "xu";
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
		// TODO
	}

	pretty(prefix="")
	{
		const r = [];
		r.push(`${prefix}${xu.cf.fg.white(" input:")} ${this.input.pretty(`${prefix}\t`).trim()}`);
		r.push(`\n${prefix}${xu.cf.fg.white("output:")} ${this.output.pretty(`${prefix}\t`).trim()}`);
		r.push(`\n${prefix}${xu.cf.fg.white("  meta:")} ${xu.inspect(this.meta).squeeze()}`);
		r.push(`\n${prefix}${xu.cf.fg.white("format:")} ${this.format.pretty(`${prefix}\t`).trim()}`);
		r.push(`\n${prefix}${xu.cf.fg.white("    id:")} ${this.id.pretty(`${prefix}\t`).trim()}`);
		r.push(`\n${prefix}${xu.cf.fg.white("   ran:")} ${xu.cf.fg.yellowDim(this.ran.length)} programs`);
		if(this.ran.length>0)
			r.push(this.ran.map(v => v.pretty(`${prefix}\t`).join("")));
		return r.join("");
	}
}

export class DexState
{
	meta = {};
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
			original : {type : Object, required : true}

			// optional
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
		// TODO
	}

	// returns a pretty string for this DexState, useful for debugging purposes
	pretty(prefix="")
	{
		const r = [];
		r.push(printUtil.majorHeader("DexState"));
		r.push(`${prefix}${xu.cf.fg.white("         result:")} ${this.processed ? xu.cf.fg.cyan("PROCESSED") : xu.cf.fg.peach("NOT PROCESSED")} ${this.format.untouched ? xu.cf.fg.deepSkyblue("**UNTOUCHED**") : ""}`);
		r.push(`\n${prefix}${xu.cf.fg.white(" original input:")} ${this.original.input.pretty()}`);
		r.push(`\n${prefix}${xu.cf.fg.white("original output:")} ${this.original.output.pretty()}`);
		r.push(`\n${prefix}${xu.cf.fg.white("  CURRENT PHASE:")}\n${this.phase.pretty(`${prefix}\t`)}`);
		r.push(`\n${prefix}${xu.cf.fg.brown("    PAST PHASES:")} ${xu.cf.fg.yellow(this.past.length)} phases\n${this.past.map(pastPhase => pastPhase.pretty(`${prefix}\t`)).join("\n")}`);
		return r.join("");
	}
}
