import {Program} from "../../Program.js";
import {fileUtil} from "xutil";
import {path} from "std";

export class tscompInfo extends Program
{
	website  = "http://fileformats.archiveteam.org/wiki/TSComp";
	loc      = "dos";
	bin      = "TSCOMP.EXE";
	args     = r => ["-l", r.inFile({backslash : true}), ">", "..\\OUT\\DEXVERTL.TXT"];
	postExec = async r =>
	{
		const listFilePath = path.join(r.f.root, "out", "DEXVERTL.TXT");
		if(!(await fileUtil.exists(listFilePath)))
		{
			r.xlog.warn`Failed to find DEXVERTL.TXT from SWAGV.EXE execution: ${listFilePath}`;
			return;
		}

		const filenamesRaw = await fileUtil.readTextFile(listFilePath);
		r.meta.tscompFilenames = filenamesRaw.split("\n").filter(line => line.trim().startsWith("=>")).map(line => line.trim().substring(2));

		await fileUtil.unlink(listFilePath);
	};
	renameOut = false;
}
