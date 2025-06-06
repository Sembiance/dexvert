import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class decomposeSGS extends Program
{
	website = "https://www.logipole.com/konvertor-en.htm";
	loc     = "win7";
	bin     = "c:\\dexvert\\DecomposeSGS\\DecomposeSGS.exe";
	unsafe  = true;
	osData  = r => ({
		scriptPre : `
			FileCopy("c:\\in\\${path.basename(r.inFile())}", "c:\\out\\${path.basename(r.inFile())}");`,
		script : `
			$mainWindow = WindowRequire("Decompose SGS.DAT", "", 10)
			Send("c:\\out\\${path.basename(r.inFile())}")
			SendSlow("{TAB}{TAB}{TAB}")
			SendSlow("{DOWN}{DOWN}")
			SendSlow("{TAB}{END}")
			SendSlow("+{TAB}+{TAB}")
			Send("{ENTER}")
			WaitForStableDirCount("c:\\out", ${xu.SECOND*30}, ${xu.MINUTE*30})
			FileDelete("c:\\out\\${path.basename(r.inFile())}")`
	});
	renameOut = true;
}
