import {xu} from "xu";
import {Program} from "../../Program.js";


export class quarkXPress6 extends Program
{
	website  = "https://archive.org/details/quarkxpress6.1version6.1r02004";
	loc      = "win7";
	bin      = "c:\\Program Files\\Quark\\QuarkXPress 6.1\\QuarkXPress Passport.exe";
	args     = r => [r.inFile()];
	osData   = ({
		script : `
			Func MainWindowOrActivate()
				WindowDismiss("Activate QuarkXPress 6.1", "", "{TAB}{ENTER}")
				return WinActive("QuarkXPress Passport (tm)", "")
			EndFunc
			$mainWindow = CallUntil("MainWindowOrActivate", ${xu.SECOND*20})

			Func PreOpenWindows()
				WindowDismiss("[TITLE:QuarkXPress (tm)]", "Some settings saved with this project are different", "{ENTER}")
				WindowDismiss("[TITLE:QuarkXPress (tm)]", "uses fonts not installed", "{TAB}{ENTER}")
				WindowFailure("[TITLE:QuarkXPress (tm)]", "This file is not a valid Quark", -1, "{ESCAPE}")
			EndFunc
			CallUntil("PreOpenWindows", ${xu.SECOND*5})

			SendSlow("!fed")

			$exportWindow = WindowRequire("Export as PDF", "", 5)
			Send("c:\\out\\out.pdf{ENTER}")
			WinWaitClose($exportWindow, "", 15)

			Func PostExportWindows()
				WindowDismiss("[TITLE:QuarkXPress (tm)]", "Some disk files for", "{ENTER}")
			EndFunc
			CallUntil("PostExportWindows", ${xu.SECOND*5})
			WaitForStableFileSize("c:\\out\\out.pdf", ${xu.SECOND*2}, ${xu.SECOND*30})

			WinWaitActive($mainWindow, "", 10)
			
			Send("^q")
			
			$saveChangesVisible = WinWaitActive("[TITLE:QuarkXPress (tm)]", "Save changes to", 5)
			If $saveChangesVisible Not = 0 Then
				Send("n")
			EndIf`
	});
	renameOut = true;
}
