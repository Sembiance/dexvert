import {Program} from "../../Program.js";

export class trid extends Program
{
	website       = "https://mark0.net/soft-trid-e.html";
	gentooPackage = "app-arch/trid";
	gentooOverlay = "dexvert";

	bin = "trid";
	loc = "local";

	args = r => [r.input.primary.rel, "-n:5"]
	post = r =>
	{
		r.meta.matches = [];

		r.stdout.split("\n").forEach(tridLine =>
		{
			const parts = tridLine.match(/^\s*(?<confidence>\d+\.\d)% \((?<extension>[^)]+)\) (?<magic>.+) \([^)]+\)$/);
			if(!parts)
				return;
			
			const tridMatch = {confidence : +parts.groups.confidence, magic : parts.groups.magic};
			tridMatch.extensions = parts.groups.extension.includes("/") ? parts.groups.extension.split("/").map(ext => (ext.charAt(0)==="." ? "" : ".") + ext) : [parts.groups.extension];
			tridMatch.extensions.mapInPlace(ext => ext.toLowerCase());
			tridMatch.from = "trid";
			r.meta.matches.push(tridMatch);
		});
	}
}
