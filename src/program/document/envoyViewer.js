import {xu} from "xu";
import {Program} from "../../Program.js";

export class envoyViewer extends Program
{
	website  = "http://userpage.fu-berlin.de/iseler/tools/read_envoy7.htm";
	loc      = "win7";
	bin      = "c:\\Program Files\\Tumbleweed\\Programs\\envoy7.exe";
	args     = r => [r.inFile()];
	osData   = ({
		script : `
			$mainWindow = WindowRequire("Envoy Viewer", "", 10)
			Send("^p")
			$printWindow = WindowRequire("Print", "", 10)
			Send("{ENTER}")

			HandleCutePDFPrint()

			WinActivate($mainWindow)
			WinWaitActive($mainWindow, "", 10)
			SendSlow("!fx")`
	});
	renameOut = true;
	chain     = "ps2pdf";
}
