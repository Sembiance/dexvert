import {xu} from "xu";
import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";

export class dearkID extends Program
{
	website    = "https://entropymine.com/deark/";
	package    = "app-arch/deark";
	bin        = "deark";
	loc        = "local";
	args       = r => ["-l", r.inFile()];
	runOptions = ({timeout : xu.SECOND*20});	// can take a while on bigger files, so just timeout quickly
	post       = r =>
	{
		r.meta.detections = [];

		const meta = {};
		const lines = r.stdout.trim().split("\n").map(line => line.trim());
		for(const line of lines)
		{
			const prefix = ["Module", "Format"].find(v => line.startsWith(`${v}: `));
			if(!prefix)
				continue;

			meta[prefix.toLowerCase()] = line.slice(prefix.length + 2).trim();
		}

		if(!Object.keys(meta).length || meta.module==="unsupported")
			return;

		const lowConfidenceStrings =
		[
			"Invalid or unsupported ",
			"No files found to extract!",
			"This is probably not "
		];
		const confidence = lines.some(line => lowConfidenceStrings.some(v => line.includes(v))) ? 1 : 100;
		r.meta.detections.push(Detection.create({value : `deark: ${meta.module}${meta.format?.length ? ` (${meta.format})` : ""}`, confidence, from : "dearkID", file : r.f.input}));
	};
	renameOut = false;
}
