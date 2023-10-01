import {xu} from "xu";
import {Program} from "../../Program.js";

export class envoyViewer extends Program
{
	website  = "http://userpage.fu-berlin.de/iseler/tools/read_envoy7.htm";
	loc      = "winxp";
	bin      = "c:\\Program Files\\Tumbleweed\\Programs\\envoy7.exe";
	args     = r => [r.inFile()];
	osData   = ({
		script : `
			$mainWindow = WindowRequire("Envoy Viewer", "", 10)
			Send("^p")
			$printWindow = WindowRequire("Print", "", 10)
			Send("{ENTER}")

			$printToWindow = WindowRequire("Print to File", "", 10)
			Send("c:\\out\\out.ps{ENTER}")
			WinWaitClose($printToWindow, "", 10)

			WaitForStableFileSize("c:\\out\\out.ps", ${xu.SECOND*3}, ${xu.SECOND*12})

			WinActivate($mainWindow)
			WinWaitActive($mainWindow, "", 10)
			SendSlow("!fx")`
	});
	renameOut = true;
	chain     = "ps2pdf";
}
