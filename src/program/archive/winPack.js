import {xu} from "xu";
import {Program} from "../../Program.js";

export class winPack extends Program
{
	website  = "https://web.archive.org/web/20060210083422/http://snoopy81.ifrance.com/snoopy81/en/winpack.htm";
	unsafe   = true;
	loc      = "winxp";
	bin      = "c:\\dexvert\\WinPack300b\\WinPack.exe";
	args     = r => [r.inFile()];
	qemuData = ({
		dontMaximize : true,
		script : `
			$mainWindowVisible = WinWaitActive("[TITLE:WinPack; CLASS:TisMainForm]", "", 10)
			If $mainWindowVisible = 0 Then
				Local $errorVisible = WinWaitActive("Erreur", "", 5)
				If $errorVisible Not = 0 Then
					ControlClick("Erreur", "", "[TEXT:OK]")
				Else
					Local $errorTwoVisible = WinWaitActive("Avertissement", "", 5)
					If $errorTwoVisible Not = 0 Then
						ControlClick("Avertissement", "", "[TEXT:OK]")
					EndIf
				EndIf
			Else
				Sleep(1000)

				Send("!f")
				Sleep(200)
				Send("u")

				WinWaitActive("[TITLE:Browse for Folder]", "", 10)

				Sleep(1000)

				Send("{DOWN}")
				Sleep(100)
				Send("{RIGHT}")
				Sleep(100)
				Send("o")
				Sleep(200)
				Send("{ENTER}")

				WinWaitClose("[TITLE:Browse for Folder]", "", 10)

				Sleep(1000)

				Send("!f")
				Sleep(200)
				Send("x")
			EndIf

			WaitForPID("WinPack.exe", ${xu.SECOND*10})`
	});
	renameOut = false;
}
