import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class paintDotNet extends Program
{
	website = "https://archive.org/details/paint.net.4.3.12";
	loc     = "win7";
	bin     = "c:\\Program Files\\paint.net\\paintdotnet.exe";
	args    = r => [r.inFile()];
	osData  = r => ({
		timeout : xu.MIUNTE*2,
		script : `
			Func MainWindowOrFailure()
				WindowFailure("paint.net", "There was an error", -1, "{ENTER}")
				WindowDismiss("Loading..", "Extract water into separate layer?", "n")
				return WinExists("${path.basename(r.inFile())} - paint.net", "")
			EndFunc
			$mainWindow = CallUntil("MainWindowOrFailure", ${xu.SECOND*10})
			If Not $mainWindow Then
				Exit 0
			EndIf
			
			MouseClick("left", 810, 40)	; Window doesn't always "activate" so we click it
			Sleep(500)
			Send("!f")
			Send("a")
			$saveAsWindow = WindowRequire("Save As", "", 10)
			Send("{TAB}{DOWN}{HOME}{DOWN}{ENTER}")
			Send("+{TAB}c:\\out\\out.png{ENTER}")
			WinWaitClose($saveAsWindow, "", 10)
			WindowDismissWait("Save Configuration", "", 4, "{ENTER}")
			WindowDismissWait("Save", "flattened", 2, "{ENTER}")
			WaitForStableFileSize("c:\\out\\out.png", ${xu.SECOND*2}, ${xu.SECOND*14})
			Send("!f")
			Send("x")
			WindowDismissWait("Unsaved Changes", "", 2, "{DOWN}{ENTER}")`
	});
	renameOut = true;
}
