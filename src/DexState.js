import {xu, fg} from "xu";
import {printUtil} from "xutil";
import {validateClass, validateObject} from "validator";
import {FileSet} from "./FileSet.js";
import {DexFile} from "./DexFile.js";
import {Format} from "./Format.js";
import {Family} from "./Family.js";
import {Identification} from "./Identification.js";
import {flexMatch} from "./identify.js";

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
		dexPhase.family = dexPhase.format.family;

		validateClass(dexPhase, {
			// required
			f      : {type : FileSet, required : true},
			format : {type : Format, required : true},
			family : {type : Family, required : true},
			id     : {type : Identification, required : true},
			xlog   : {}
		});
		
		return dexPhase;
	}

	serialize()
	{
		const o = {};
		for(const key of ["f", "format", "family", "id"])
			o[key] = this[key].serialize();
		o.meta = xu.parseJSON(JSON.stringify(this.meta), {});
		o.ran = this.ran.map(v => v.serialize());
		for(const key of ["converter", "err"])
		{
			if(this[key])
				o[key] = this[key];
		}

		return o;
	}

	pretty(prefix="")
	{
		const r = [];
		r.push(`${prefix}${xu.colon("format")}${this.format.pretty(`${prefix}\t`).trim()}`);
		if(this.xlog.atLeast("info"))
			r.push(`\n${prefix}${xu.colon("  meta")}${printUtil.inspect(this.meta).squeeze()}`);
		if(this.xlog.atLeast("info"))
			r.push(`\n${prefix}${xu.colon("    id")}${this.id.pretty(`${prefix}\t`).trim()}`);
		if(this.xlog.atLeast("debug"))
			r.push(`\n${prefix}${xu.colon("     f")}${this.f.pretty(`${prefix}\t`).trim()}`);
		if(this.xlog.atLeast("info"))
		{
			r.push(`\n${prefix}${xu.colon("   ran")}${fg.yellowDim(this.ran.length)} program${this.ran.length===1 ? "" : "s"}`);
			if(this.ran.length>0)
				r.push(this.ran.map(v => `\n${v.pretty(`${prefix}\t`)}`).join(""));
		}
		return r.join("");
	}
}

export class DexState
{
	phase = null;
	past = [];
	idMeta = {};
	baseKeys = Object.keys(this);

	// builder to get around the fact that constructors can't be async
	static create(o)
	{
		const dexState = new this();
		Object.assign(dexState, o);

		validateClass(dexState, {
			// required
			original : {type : Object, required : true},
			ids      : {type : [Identification], required : true, allowEmpty : true},
			xlog   : {}
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
		const dexPhase = o instanceof DexPhase ? o : DexPhase.create({xlog : this.xlog, ...o});
		if(this.phase)
			this.past.push(this.phase);
		this.phase = dexPhase;
		return dexPhase;
	}

	// convenience methods to access current phase properties
	get f() { return this.phase?.f; }
	get format() { return this.phase?.format; }
	get meta() { return this.phase?.meta; }
	get ran() { return this.phase?.ran; }
	get id() { return this.phase?.id; }

	hasMagics(magics, {strong, format}={})
	{
		return (strong ? this.ids.filter(id => !id.weak && (!format || !Array.isArray(format.weakMagic) || !format.weakMagic.some(m => flexMatch(id.magic, m)))) : this.ids).some(id => Array.force(magics).some(matchAgainst => flexMatch(id.magic, matchAgainst)));
	}

	serialize()
	{
		const o = {};
		o.original = Object.fromEntries(Object.entries(this.original).map(([k, v]) => ([k, v.serialize()])));
		o.ids = this.ids.map(v => v.serialize());
		if(this.phase)
			o.phase = this.phase.serialize();
		o.past = this.past.map(v => v.serialize());
		o.processed = !!this.processed;
		if(Object.keys(this.idMeta).length>0)
			o.idMeta = this.idMeta;
		if(this.created)
			o.created = this.created.serialize();
		for(const key of ["duration"])
		{
			if(this[key])
				o[key] = this[key];
		}
		return o;
	}

	// returns a pretty string for this DexState, useful for debugging purposes
	pretty(prefix="")
	{
		const r = [];
		if(this.xlog.atLeast("info") && this.past.length>0)
		{
			r.push(`\n${printUtil.majorHeader("DexState")}`);
			r.push(`\n${prefix}${xu.colon(fg.brown(" PAST PHASES"))}${fg.yellowDim(this.past.length)} phase${this.past.length===1 ? "" : "s"}\n${this.past.map(pastPhase => pastPhase.pretty(`${prefix}\t`)).join("\n\n")}`);
		}

		r.push(`\n${prefix}${this.past.length>0 ? printUtil.minorHeader("ACTIVE PHASE") : ""}${this.phase ? this.phase.pretty(`${prefix}\t`) : ""}`);
		
		r.push(`\n${fg.cyan("-".repeat(100))}`);
		r.push(`\n${prefix}${xu.colon("  result")}${xu.c.bold}${this.processed ? fg.green("**PROCESSED**") : fg.red(`${xu.c.blink}**NOT PROCESSED**`)}`);
		if(this.untouched)
			r.push(` ${fg.deepSkyblue("**UNTOUCHED**")}`);

		if(this.duration)
			r.push(`  ${xu.paren(`took ${fg.yellow((this.duration/xu.SECOND).secondsAsHumanReadable())}`)}`);
		if(this.processed)
			r.push(`\n${prefix}${xu.colon("  format")}${this.format.pretty()}`);
		r.push(`\n${prefix}${xu.colon(" orig in")}${this.original.input.pretty()}`);
		r.push(`\n${prefix}${xu.colon("orig out")}${this.original.output.pretty()}`);
		if(this.processed)
			r.push(`\n${prefix}${xu.colon("    meta")}${printUtil.inspect(this.meta).squeeze()}`);
		if(Object.keys(this.idMeta).length>0)
			r.push(`\n${prefix}${xu.colon("  idMeta")}${printUtil.inspect(this.idMeta).squeeze()}`);
		if(this.created)
			r.push(`\n${prefix}${xu.colon(" created")}${this.created.pretty(`${prefix}`).trim()}`);
		return r.join("");
	}
}
