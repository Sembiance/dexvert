import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";

export class trid extends Program
{
	website       = "https://mark0.net/soft-trid-e.html";
	gentooPackage = "app-arch/trid";
	gentooOverlay = "dexvert";

	bin = "trid";
	loc = "local";

	args = r => [r.input.main.rel, "-n:5"]
	post = r =>
	{
		r.meta.detections = [];

		r.stdout.split("\n").forEach(tridLine =>
		{
			const parts = tridLine.match(/^\s*(?<confidence>\d+\.\d)% \((?<extension>[^)]+)\) (?<value>.+) \([^)]+\)$/);
			if(!parts)
				return;
			
			const tridMatch = {confidence : +parts.groups.confidence, value : parts.groups.value, file : r.input.main};
			tridMatch.extensions = parts.groups.extension.includes("/") ? parts.groups.extension.split("/").map(ext => (ext.charAt(0)==="." ? "" : ".") + ext) : [parts.groups.extension];
			tridMatch.extensions.mapInPlace(ext => ext.toLowerCase());
			tridMatch.from = "trid";
			r.meta.detections.push(Detection.create(tridMatch));
		});
	}
}
