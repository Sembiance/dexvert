import {Program} from "../../Program.js";

export class replica extends Program
{
	website  = "https://gondwanaland.com/meta/history/";
	unsafe   = true;
	loc      = "win2k";
	bin      = "c:\\REPLICA\\REPLICA.EXE";
	args     = r => [r.inFile()];
	osData   = ({
		script : `
			$mainWindow = WindowRequire("[CLASS:DPMDIFrameClass]", "", 15)
		
			SendSlow("!fp")

			$printWindow = WindowRequire("Print", "", 5)
			Send("{ENTER}")

			$savePDFWindow = WindowRequire("Save PDF File As", "", 5)
			Send("c:\\out\\out.pdf{ENTER}")
			WinWaitClose($savePDFWindow)
			
			$pleaseWaitWindow = WindowRequire("Please Wait", "", 5)
			WinWaitClose($pleaseWaitWindow)

			WinWaitActive($mainWindow, "", 5)

			SendSlow("!fx")`
	});
	renameOut = true;
}
