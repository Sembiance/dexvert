import {xu} from "xu";
import {printUtil} from "xutil";
import {validateClass, validateObject} from "./validate.js";
import {FileSet} from "./FileSet.js";
import {DexFile} from "./DexFile.js";
import {Format} from "./Format.js";
import {Identification} from "./Identification.js";

export class DexPhase
{
	// builder to get around the fact that constructors can't be async
	constructor({allowNew}) { if(!allowNew) { throw new Error(`Use static ${this.constructor.name}.create() instead`); } }	// eslint-disable-line curly
	static create(o)
	{
		const dexPhase = new this({allowNew : true});
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

	pretty(prefix="")
	{
		const r = [];
		r.push(`${prefix}${xu.cf.fg.white(" input:")} ${this.input.pretty(`${prefix}\t`)}`);
		r.push(`\n${prefix}${xu.cf.fg.white("output:")} ${this.output.pretty(`${prefix}\t`)}`);
		r.push(`\n${prefix}${xu.cf.fg.white("format:")} ${this.format.pretty(`${prefix}\t`)}`);
		r.push(`\n${prefix}${xu.cf.fg.white("    id:")} ${this.id.pretty(`${prefix}\t`)}`);
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
	constructor({allowNew}) { if(!allowNew) { throw new Error(`Use static ${this.constructor.name}.create() instead`); } }	// eslint-disable-line curly
	static create(o)
	{
		const dexState = new this({allowNew : true});
		Object.assign(dexState, o);
		dexState.meta.size = dexState.original.input.size;
		dexState.meta.ts = dexState.original.input.ts;

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
	phase(o)
	{
		const dexPhase = o instanceof DexPhase ? o : DexPhase.create(o);
		if(this.phase)
			this.past.push(this.phase);
		this.phase = dexPhase;
	}

	// convenience methods to access current phase properties
	get input() { return this.phase.input; }
	get output() { return this.phase.output; }
	get format() { return this.phase.format; }
	get id() { return this.phase.id; }

	// returns a pretty string for this DexState, useful for debugging purposes
	pretty(prefix="")
	{
		const r = [];
		r.push(printUtil.majorHeader("DexState"));
		r.push(`${prefix}${xu.cf.fg.white("  input:")} ${this.original.input.absolute}`);
		r.push(`\n${prefix}${xu.cf.fg.white(" output:")} ${this.original.output.absolute}`);
		r.push(`\n${prefix}${xu.cf.fg.white("    cwd:")} ${this.input.root}`);
		r.push(`\n${prefix}${xu.cf.fg.white("CURRENT:")} ${this.phase.pretty()}`);
		const meta = Deno.inspect(this.meta, {colors : true, compact : true, depth : 7, iterableLimit : 150, showProxy : false, sorted : false, trailingComma : false, getters : false, showHidden : false});
		r.push(`\n${prefix}${xu.cf.fg.white("   meta:")}${meta.includes("\n") ? "\n" : " "}${meta}`);
		r.push(`\n${prefix}${xu.cf.fg.white(" result:")} ${this.format.untouched ? xu.cf.fg.peach("UNTOUCHED") : "TODO"}`);
		r.push(`\n${prefix}${xu.cf.fg.brown("   PAST:")} ${this.past.map(pastPhase => pastPhase.pretty("\t")).join("\n")}`);
		return r.join("");
	}
}
