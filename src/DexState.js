import {xu} from "xu";
import {printUtil} from "xutil";

export class DexState
{
	meta = {};
	
	// builder to get around the fact that constructors can't be async
	constructor({allowNew}) { if(!allowNew) { throw new Error(`Use static ${this.constructor.name}.create() instead`); } }	// eslint-disable-line curly
	static create(o)
	{
		const dexState = new this({allowNew : true});
		Object.assign(dexState, o);
		dexState.meta.size = dexState.input.original.size;
		dexState.meta.ts = dexState.input.original.ts;
		return dexState;
	}

	// returns a pretty string for this DexState, useful for debugging purposes
	pretty()
	{
		const r = [];
		r.push(printUtil.majorHeader("DexState"));
		r.push(`${xu.cf.fg.white(" input:")} ${this.input.original.absolute}`);
		r.push(`\n${xu.cf.fg.white("output:")} ${this.output.original.absolute}`);
		r.push(`\n${xu.cf.fg.white("   cwd:")} ${this.input.root}`);
		r.push(`\n${xu.cf.fg.white("format:")} ${this.format.pretty()}`);
		const meta = Deno.inspect(this.meta, {colors : true, compact : true, depth : 7, iterableLimit : 150, showProxy : false, sorted : false, trailingComma : false, getters : false, showHidden : false});
		r.push(`\n${xu.cf.fg.white("  meta:")}${meta.includes("\n") ? "\n" : " "}${meta}`);
		r.push(`\n${xu.cf.fg.white("result:")} ${this.format.untouched ? xu.cf.fg.peach("UNTOUCHED") : "TODO"}`);
		return r.join("");
	}
}
