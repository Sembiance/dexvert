import {xu} from "xu";
import {Program} from "../../Program.js";

export class wordStar extends Program
{
	website  = "https://en.wikipedia.org/wiki/WordStar";
	loc      = "win2k";
	unsafe   = true;
	bin      = "c:\\WSWIN\\WSWIN.EXE";
	args     = r => [r.inFile()];
	osData   = ({
		script : `
			Func DismissWarnings()
				WindowDismiss("[TITLE:Error]", "", "{ENTER}")
				WindowDismiss("[TITLE:Warning]", "", "{END}{ENTER}")
				WindowDismiss("[TITLE:Error]", "", "{ENTER}")
				WindowDismiss("[TITLE:Warning]", "", "{HOME}{ENTER}")
				WindowDismiss("[TITLE:WSWin 2.0]", "No printer is installed", "{ENTER}")
			EndFunc
			CallUntil("DismissWarnings", ${xu.SECOND*3})

			$mainWindow = WindowRequire("[TITLE:WSWin 2.0]", "", 10)

			Send("^p")
			$printWindow = WindowRequire("Print", "", 10)
			Send("{ENTER}")
		
			$savePDFWindow = WindowRequire("Save PDF File As", "", 5)
			Send("c:\\out\\out.pdf{ENTER}")
			WinWaitClose($savePDFWindow)

			; There are some windows in-between but they go too fast, so we just sleep
			WinWaitClose("Print Status", "", 10)
			WinWaitActive($mainWindow, "", 15)

			; This is the old export to .txt code
			;Send("^+e")
			;WinWaitActive("[TITLE:Export]", "", 10)
			;Sleep(200)
			;Send("c:\\out\\out.txt{TAB}{TAB}{TAB}{TAB}ansi{ENTER}")
			;WinWaitClose("[TITLE:Export]", "", 10)

			Send("^q")
			WindowDismissWait("[TITLE:WSWin 2.0]", "Do you want to save", 3, "n")`
	});
	renameOut = true;
}
