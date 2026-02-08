import {xu} from "xu";
import {Program} from "../../Program.js";

export class spinBakerSBX extends Program
{
	website = "http://web.archive.org/web/20001218041900/www.spinnerbaker.com/sbx.htm";
	loc     = "winxp";
	bin     = "c:\\Program Files\\Sbx\\Sbx.exe";
	args    = r => [r.inFile()];
	osData  = ({
		script : `
			Func HandleNagScreen()
				$nagWindow = WindowRequire("SBX - Version 1.4 - Unregistered copy", "", 10)
				Sleep(6500)
				Send("{ENTER}")
				WinWaitClose($nagWindow, "", 10)
			EndFunc

			Func MainWindowOrFailure()
				WindowFailure("SBX", "File is not an SB archive", -1, "{ENTER}")
				return WinActive("in.sb - SBX", "")
			EndFunc

			HandleNagScreen()

			$mainWindow = CallUntil("MainWindowOrFailure", ${xu.SECOND*15})
			If Not $mainWindow Then
				Exit 0
			EndIf

			Send("{UP}+{END}")
			SendSlow("!ce")

			$extractWindow = WindowRequire("Extract to:", "", 10)
			SendSlow("{UP}{ENTER}")
			Send("out{ENTER}{ENTER}")

			WinWaitClose($extractWindow, "", 10)
			WinWaitActive($mainWindow, "", 10)
			
			WaitForStableDirCount("c:\\out", ${xu.SECOND*10}, ${xu.MINUTE*2})

			SendSlow("!fx")`
	});
	renameOut = false;
}
