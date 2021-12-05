import {xu} from "xu";
import {Program} from "../../Program.js";

export class soxi extends Program
{
	website = "http://sox.sourceforge.net";
	package = "media-sound/sox";
	bin     = "soxi";
	args    = r => [r.inFile()];
	post    = r =>
	{
		if(r.stdout.includes("can't open input file"))
			return;
		
		r.stdout.trim().split("\n").forEach(line =>
		{
			const {key, val} = (line.trim().match(/^(?<key>[^:]+)\s*:\s*(?<val>.+)$/) || {groups : {}}).groups;
			if(key && val && !["Input File", "Comments", "File Size"].some(v => key.trim().startsWith(v)))
			{
				const properKey = key.trim().toCamelCase();
				if(properKey==="duration")
				{
					const parts = val.trim().match(/^(?<hour>\d+):(?<minute>\d+):(?<second>\d+)\.(?<ms>\d*)/).groups;
					r.meta[properKey] = [...["hour", "minute", "second"].map(v => (xu[v.toUpperCase()]*(+parts[v]))), (+parts.ms)].sum();
				}
				else
				{
					r.meta[properKey] = (["channels", "sampleRate"].includes(properKey) ? +val.trim() : val.trim());
				}
			}
		});
	};
}
