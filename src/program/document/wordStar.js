import {xu} from "xu";
import {Program} from "../../Program.js";

export class wordStar extends Program
{
	website  = "https://en.wikipedia.org/wiki/WordStar";
	loc      = "win2k";
	unsafe   = true;
	bin      = "c:\\WSWIN\\WSWIN.EXE";
	args     = r => [r.inFile()];
	qemuData = ({
		alsoKill : ["ntvdm.exe"],	// Sometimes the program is still running, but it's not under WSWIN.EXE so we have to kill this
		script   : `
			WinWaitActive("[TITLE:WSWin 2.0]", "", 10)

			Func DismissWarnings()
				WindowDismiss("[TITLE:Warning]", "", "{ENTER}")
				WindowDismiss("[TITLE:WSWin 2.0]", "No printer is installed", "{ENTER}")
			EndFunc
			CallUntil("DismissWarnings", ${xu.SECOND*3})

			Send("^+e")

			WinWaitActive("[TITLE:Export]", "", 10)

			Sleep(200)
			Send("c:\\out\\out.txt{TAB}{TAB}{TAB}{TAB}ansi{ENTER}")
			WinWaitClose("[TITLE:Export]", "", 10)

			Send("^q")

			$saveChangesVisible = WinWaitActive("[TITLE:WSWin 2.0]", "Do you want to save", 5)
			If $saveChangesVisible Not = 0 Then
				Send("n")
			EndIf
			
			WinWaitClose("[TITLE:WSWin 2.0]", "", 10)`
	});
	renameOut = true;
}
