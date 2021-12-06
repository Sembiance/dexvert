import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";
import {fileUtil} from "xutil";

export class trid extends Program
{
	website = "https://mark0.net/soft-trid-e.html";
	package = "app-arch/trid";
	bin     = "trid";
	loc     = "local";

	pre = async r =>
	{
		// trid is SUPER sensitive to certain filenames, so we copy it to a tmp file and run trid against that
		r.tridTmpFilePath = await fileUtil.genTempPath();
		await Deno.copyFile(r.inFile({absolute : true}), r.tridTmpFilePath);
	};

	args = r => [r.tridTmpFilePath, "-n:5"];
	post = async r =>
	{
		await fileUtil.unlink(r.tridTmpFilePath);

		r.meta.detections = [];

		r.stdout.split("\n").forEach(tridLine =>
		{
			const parts = tridLine.match(/^\s*(?<confidence>\d+\.\d)% \((?<extension>[^)]+)\) (?<value>.+) \([^)]+\)$/);
			if(!parts)
				return;
			
			const tridMatch = {confidence : +parts.groups.confidence, value : parts.groups.value, file : r.f.input};
			tridMatch.extensions = parts.groups.extension.includes("/") ? parts.groups.extension.split("/").map(ext => (ext.charAt(0)==="." ? "" : ".") + ext) : [parts.groups.extension];
			tridMatch.extensions.mapInPlace(ext => ext.toLowerCase());
			tridMatch.from = "trid";
			r.meta.detections.push(Detection.create(tridMatch));
		});
	};
}
