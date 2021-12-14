import {Program} from "../../Program.js";

export class soxStat extends Program
{
	website = "http://sox.sourceforge.net";
	package = "media-sound/sox";
	bin     = "sox";
	args    = r => [r.inFile(), "-n", "stat"];
	post    = r =>
	{
		const meta = r.stderr.trim().split("\n").reduce((result, line="") =>	// eslint-disable-line unicorn/prefer-object-from-entries
		{
			const parts = line.split(":");
			if(!parts || parts.length!==2)
				return result;
			result[parts[0].split(" ").filter(v => !!v).map(v => v.trim()).join(" ")] = parts[1].trim();
			return result;
		}, {});

		Object.assign(r.meta, meta);
	};
	renameOut = false;
}
