import {xu, fg} from "xu";
import {validateClass} from "./validate.js";
import {DexState} from "./DexState.js";
import {Program} from "./Program.js";
import {identify} from "./identify.js";

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
		const verbose = this.dexState.verbose;
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
				const programOptions = {flags, verbose : this.dexState.verbose, originalInput : this.dexState.original.input};
				const r = await Program.runProgram(programid, this.dexState.f, programOptions);
				this.dexState.ran.push(r);

				// verify output files
				for(const newFile of this.dexState.f.files.new || [])
				{
					const isValid = await this.dexState.format.family.verify(newFile, await identify(newFile, {verbose}), {verbose, programid, dexState : this.dexState});
					if(!isValid)
					{
						if(verbose>=3)
							xu.log`${fg.red("DELETING OUTPUT FILE")} ${newFile.pretty()} due to failing verification from ${this.dexState.format.family.pretty()} family`;
						await Deno.remove(newFile.absolute);
					}
					else
					{
						await this.dexState.f.add("output", newFile);
					}
				}
				this.dexState.f.removeType("new");
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
