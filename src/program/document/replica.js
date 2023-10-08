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
			$mainWindow = WindowRequire("[CLASS:DPMDIFrameClass]", "", 20)
		
			SendSlow("!fp")

			$printWindow = WindowRequire("Print", "", 7)
			Send("{ENTER}")

			$savePDFWindow = WindowRequire("Save PDF File As", "", 7)
			SendSlow("c:\\out\\out.pdf{ENTER}")
			WinWaitClose($savePDFWindow, "", 5)
			
			$pleaseWaitWindow = WindowRequire("Please Wait", "", 7)
			WinWaitClose($pleaseWaitWindow, "", 5)

			WinWaitActive($mainWindow, "", 5)

			SendSlow("!fx")`
	});
	renameOut = true;
}
