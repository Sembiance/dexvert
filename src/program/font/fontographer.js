import {xu} from "xu";
import {Program} from "../../Program.js";

export class fontographer extends Program
{
	website  = "https://www.fontlab.com/font-editor/fontographer/";
	loc      = "winxp";
	bin      = "c:\\Program Files\\Fontlab\\Fontographer 5\\Fontographer 5.exe";
	args     = r => [r.inFile()];
	osData   = ({
		script : `
			$mainWindow = WindowRequire("Fontographer 5.2", "", 10)
			$fontWindowControl = WaitForControl($mainWindow, "", "[CLASS:FONTWIN]", ${xu.SECOND*10});
			If $fontWindowControl = 0 Then
				SendSlow("!fx")
				Exit 0
			EndIf
			Sleep(1000)
			SendSlow("!fg")

			$generateWindow = WindowRequire("Generate Font Files", "", 10)
			Sleep(100)
			ControlSetText($generateWindow, "", "[CLASS:Edit; INSTANCE:2]", "c:\\out")
			SendSlow("{ENTER}")

			WinWaitClose($generateWindow, "", 10)
			
			$pleaseWaitWindow = WinWaitActive("Please Wait", "", 3)
			WinWaitClose($pleaseWaitWindow, "", 20)

			SendSlow("!fx")`
	});
	renameOut = false;
	chain     = "dexvert[asFormat:font/otf]";
}
