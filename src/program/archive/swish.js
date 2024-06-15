import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class swish extends Program
{
	website = "https://archive.org/details/onyxdvd-16";
	bin     = "c:\\Program Files\\SWiSH v2.0\\Swish2.exe";
	args    = r => [r.inFile()];
	loc     = "win2k";
	osData  = r => ({
		script : `
			Func MainWindowOrFailure()
				WindowFailure("SWiSH", "This file appears to have been", -1, "{ENTER}")
				return WinActive("${path.basename(r.inFile())} - SWiSH 2.01", "")
			EndFunc
			$mainWindow = CallUntil("MainWindowOrFailure", ${xu.SECOND*30})
			If Not $mainWindow Then
				Exit 0
			EndIf

			Send("!f")
			Send("es")

			$exportWindow = WindowRequire("Export to SWF", "", 10)
			Send("c:\\out\\out.swf{ENTER}")
			WinWaitClose($exportWindow, "", 30)
			WaitForStableFileSize("c:\\out\\out.swf", ${xu.SECOND*2}, ${xu.SECOND*30})

			Send("!f")
			Send("x")`
	});
	renameOut = false;
	chain     = "dexvert[asFormat:archive/swf]";
}
