import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class pageMaker7QuarkConverter extends Program
{
	website  = "https://archive.org/details/adobe-page-maker-7.0-with-serial-key-pwd-12345_20221219";
	loc      = "winxp";
	bin      = "c:\\Program Files\\Adobe\\PageMaker 7.0\\Converter for MSP_QXP\\MSPublisher_Quark Converter.exe";
	osData   = r => ({
		dontMaximize : true,
		script : `
			$mainWindow = WindowRequire("Converter for Microsoft", "", 10)
			SendSlow("!os")
			$chooseDestinationWindow = WindowRequire("Choose Destination", "", 5)
			Send("+{TAB}")
			Sleep(500)
			Send("+{TAB}")
			Sleep(500)
			Send("+{TAB}")
			Sleep(500)
			SendSlow("{DOWN}{HOME}{DOWN}{DOWN}{DOWN}{DOWN}{TAB}{TAB}{DOWN}out{ENTER}{TAB}{ENTER}");
			WinWaitClose($chooseDestinationWindow, "", 5)

			Send("^o")
			$selectFileWindow = WindowRequire("Select Files to Convert", "", 5)
			Send("c:\\in\\${path.basename(r.inFile())}{ENTER}")
			WinWaitClose($selectFileWindow, "", 5)

			SendSlow("{TAB}{ENTER}")

			; It doesn't open a window, so check for the Converting text
			WaitForControl($mainWindow, "", "[CLASS:Static; TEXT:Converting  1 of 1]", 5)

			Func WaitForFinish()
				If ControlGetHandle($mainWindow, "", "[CLASS:Static; TEXT:Converting  1 of 1]") = 0 Then
					Return 1
				EndIf
			EndFunc
			CallUntil("WaitForFinish", ${xu.MINUTE*2})

			SendSlow("!fx")`
	});
	renameOut = true;
	chain     = "dexvert[asFormat:document/pageMaker]";
}
