import {Program} from "../../Program.js";
import {fileUtil} from "xutil";
import {path} from "std";

export class softlibList extends Program
{
	website  = "http://files.shikadi.net/moddingwiki/tools/kdreams/softlib.exe";
	loc      = "dos";
	bin      = "SOFTLIB.EXE";
	flags   = {
		outDirname : "Dirname where the DEXVERTL.TXT file should be output, overrides default"
	};
	args     = r => ["V", r.inFile({backslash : true}), ">", `..\\${r.flags.outDirname || r.f.outDir.base}\\DEXVERTL.TXT`];
	postExec = async r =>
	{
		const listFilePath = path.join(r.f.root, r.flags.outDirname || r.f.outDir.base, "DEXVERTL.TXT");
		if(!(await fileUtil.exists(listFilePath)))
		{
			r.xlog.warn`Failed to find DEXVERTL.TXT from SWAGV.EXE execution: ${listFilePath}`;
			return;
		}

		const filenamesRaw = await fileUtil.readTextFile(listFilePath);
		r.meta.softlibFilenames = filenamesRaw.split("\n").filter(line => (/^\d{5}\s/).test(line.trim())).map(line => line.trim().split(" ").filter(v => !!v)[1]);

		await fileUtil.unlink(listFilePath);
	};
	renameOut = false;
}
