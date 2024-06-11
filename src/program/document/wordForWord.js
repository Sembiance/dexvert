import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class wordForWord extends Program
{
	website  = "https://archive.org/details/adobe-file-utilities-mac-win-1996";
	loc      = "win2k";
	bin      = "c:\\dexvert\\WFW\\WFWWIN32.EXE";
	args     = r => [r.inFile()];
	osData   = r => ({
		script : `
			$mainWindow = WindowRequire("WORD FOR WORD", "", 10)
			Sleep(500)
			Send("{TAB}{END}")
			Send("{ENTER}")
			Send("!f")
			Send("b")
			WaitForStableFileSize("c:\\out\\${path.basename(r.inFile(), path.extname(r.inFile()))}.new", ${xu.SECOND*2}, ${xu.SECOND*10})
			Send("{ENTER}")
			Send("!f")
			Send("x")`
	});
	chain     = "dexvert[asFormat:document/rtf]";
	renameOut = true;
}
