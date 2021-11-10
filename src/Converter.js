import {xu} from "xu";
import {validateClass} from "./validate.js";
import {DexState} from "./DexState.js";
import {Program} from "./Program.js";

export class Converter
{
	// builder to get around the fact that constructors can't be async
	static create(dexState, value)
	{
		const converter = new this();
		converter.dexState = dexState;
		converter.value = value;

		validateClass(converter, {
			// required
			dexState : {type : DexState, required : true},
			value    : {type : "string", required : true}
		});
		
		return converter;
	}

	async run()
	{
		const chain = this.value.split("->").map(v => v.trim());	// deark[keepAsGIF][outputFormat:GIF][fps:60] & nconvert -> word97
		for(const link of chain)	// deark[keepAsGIF][outputFormat:GIF][fps:60] & nconvert
		{
			const progs = link.split("&").map(v => v.trim());
			for(const prog of progs)	// deark[keepAsGIF][outputFormat:GIF][fps:60]
			{
				const {programid, flagsRaw=""} = prog.match(/^\s*(?<programid>[^[]+)(?<flagsRaw>.*)$/).groups;
				const flags = Object.fromEntries((flagsRaw.match(/\[[^:\]]+:?[^\]]*]/g) || []).map(flag =>
				{
					const {name, val} = flag.match(/\[(?<name>[^:\]]+):?(?<val>[^\]]*)]/)?.groups || {};
					return (name ? [name, (val.length>0 ? (val.isNumber() ? +val : val) : true)] : null);
				}).filter(v => !!v));

				// run prog
				const r = await Program.runProgram(programid, this.dexState.input, this.dexState.output, {flags, verbose : this.dexState.verbose, originalInput : this.dexState.original.input, outExt : this.dexState.format.family.outExt});
			}
		}
	}

	serialize()
	{
		const o = {};
		return o;
	}

	pretty(prefix="")
	{
		const r = [];
		return r.join("");
	}
}




