import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";
import {fileUtil} from "xutil";
import {detectPreRename} from "../../dexUtil.js";

export class trid extends Program
{
	website = "https://mark0.net/soft-trid-e.html";
	package = "app-arch/trid";
	bin     = "trid";
	loc     = "local";
	pre     = detectPreRename;
	args    = r => ["-n", "5", r.detectTmpFilePath];
	post    = async r =>
	{
		await fileUtil.unlink(r.detectTmpFilePath);

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
	renameOut = false;
}
