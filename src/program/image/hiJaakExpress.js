import {xu} from "xu";
import {Program} from "../../Program.js";

export class hiJaakExpress extends Program
{
	website  = "https://archive.org/details/hijaak-express";
	loc      = "win2k";
	bin      = "c:\\Program Files\\IMSI\\HiJaak Express\\bin\\hjcvt32.exe";
	args     = r => [r.inFile()];
	osData   = ({
		script : `
			Func MainWindowOrFailure()
				WindowFailure("HiJaak Convert", "Error", 2, "{ESCAPE}")
				WindowFailure("Application Error", "", -1, "{ENTER}")
				return WinActive("HiJaak Convert", "Save as")
			EndFunc
			$mainWindow = CallUntil("MainWindowOrFailure", ${xu.SECOND*10})
			If Not $mainWindow Then
				Exit 0
			EndIf
			
			Send("c:\\out\\out.bmp{ENTER}")
			AutoItSetOption("WinTitleMatchMode", 2)
			$failureWindow = WinWait("Application Error", "", 10)
			If $failureWindow Then
				Exit 0
			EndIf
			WaitForStableFileSize("c:\\out\\out.bmp", ${xu.SECOND*3}, ${xu.SECOND*15})
			WinWaitClose($mainWindow, "", 10)
			
			KillAll("loco.exe")
			KillAll("Hijaak.exe")
			KillAll("hjcvt32.exe")

			Send("{ESCAPE}")
			Send("{ESCAPE}")
			Send("{ESCAPE}")
			Send("{ESCAPE}")
			Send("{ESCAPE}")`
	});
	renameOut = true;
	chain     = "convert";
}
