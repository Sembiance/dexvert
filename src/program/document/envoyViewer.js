import {Program} from "../../Program.js";

export class envoyViewer extends Program
{
	website  = "http://userpage.fu-berlin.de/iseler/tools/read_envoy7.htm";
	loc      = "winxp";
	bin      = "c:\\Program Files\\Tumbleweed\\Programs\\envoy7.exe";
	args     = r => [r.inFile()];
	osData   = ({
		script : `
			$mainWindow = WinWaitActive("Envoy Viewer", "", 10)
			If $mainWindow Not = 0 Then
				Send("^p")
				WinWaitActive("Print", "", 10)
				Send("{ENTER}")
				WinWaitActive("Print to File", "", 10)
				Send("c:\\out\\out.ps{ENTER}")
				WinWaitClose("Print to File", "", 10)
				Sleep(5000)
				WinActivate($mainWindow)
				WinWaitActive($mainWindow, "", 10)
				SendSlow("!fx")
			EndIf`
	});
	renameOut = true;
	chain     = "ps2pdf";
}
