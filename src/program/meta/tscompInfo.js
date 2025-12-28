import {Program} from "../../Program.js";
import {fileUtil} from "xutil";
import {path} from "std";

export class tscompInfo extends Program
{
	website  = "http://fileformats.archiveteam.org/wiki/TSComp";
	loc      = "dos";
	bin      = "TSCOMP.EXE";
	flags   = {
		outDirname : "Dirname where the DEXVERTL.TXT file should be output, overrides default"
	};
	args     = r => ["-l", r.inFile({backslash : true}), ">", `..\\${r.flags.outDirname || r.f.outDir.base}\\DEXVERTL.TXT`];
	postExec = async r =>
	{
		const listFilePath = path.join(r.f.root, r.flags.outDirname || r.f.outDir.base, "DEXVERTL.TXT");
		if(!await fileUtil.exists(listFilePath))
		{
			r.xlog.warn`Failed to find DEXVERTL.TXT from TSCOMP.EXE execution: ${listFilePath}`;
			return;
		}

		const filenamesRaw = await fileUtil.readTextFile(listFilePath);
		r.meta.tscompFilenames = filenamesRaw.split("\n").filter(line => line.trim().startsWith("=>")).map(line => line.trim().substring(2));

		await fileUtil.unlink(listFilePath);
	};
	renameOut = false;
}
