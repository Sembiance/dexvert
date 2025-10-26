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
		try
		{
			if(await fileUtil.exists(r.inFile({absolute : true})))
				await Deno.copyFile(r.inFile({absolute : true}), r.tridTmpFilePath);	// can't use a symlink as that changes the file type, hard link can't be used across different filesystems, so we have to copy. sad.
		}
		catch(err)
		{
			r.xlog.warn`Failed to copy file to tmp file for trid: ${err}`;
		}
	};

	args = r => ["-n", "5", r.tridTmpFilePath];
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
	renameOut = false;
}
