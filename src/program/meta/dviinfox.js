import {Program} from "../../Program.js";

export class dviinfox extends Program
{
	website = "http://tug.org/texlive/";
	package = "app-text/texlive";
	bin     = "dviinfox";
	args    = r => [r.inFile()];
	post    = r =>
	{
		const meta = {};
		r.stdout.trim().split("\n").forEach(line =>
		{
			const {key, val} = (line.trim().match(/^\s*(?<key>[^:]+):\s*"?(?<val>[^"]+)"?$/) || {groups : {}}).groups;
			if(!key || !val || key.trim().length===0 || val.trim().length===0)
				return;

			meta[key.trim().toCamelCase()] = val.trim();
		});

		Object.assign(r.meta, meta);
	};
	renameOut = false;
}
