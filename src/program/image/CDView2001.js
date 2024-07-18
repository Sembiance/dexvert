import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class CDView2001 extends Program
{
	website  = "https://archive.org/details/cdview-2001";
	loc      = "win2k";
	bin      = "c:\\dexvert\\CDView2001\\CDView2001_patched.exe";
	osData   = r => ({
		scriptPre : `
			DirRemove("c:\\dexvert\\CDView2001\\asie01", 1)
			DirCreate("c:\\dexvert\\CDView2001\\asie01")
			FileCopy("c:\\in\\${path.basename(r.inFile())}", "c:\\dexvert\\CDView2001\\asie01\\${path.basename(r.inFile())}");`,
		script   : `
			$codeWindow = WindowRequire("Validation du code", "", 10)
			Send("a{ENTER}")
			WinWaitClose($codeWindow, "", 5)
			MouseClick("left", 100, 50)
			SendSlow("${"{TAB}".repeat(9)}")
			Send("{SPACE}")
			$saveWindow = WindowRequire("Save As", "", 10)
			Send("c:\\out\\out.bmp{ENTER}")
			WinWaitClose($saveWindow, "", 10)`
	});
	renameOut = true;
	chain     = "dexvert[asFormat:image/bmp]";
}
