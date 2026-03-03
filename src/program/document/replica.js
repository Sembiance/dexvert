import {xu} from "xu";
import {Program} from "../../Program.js";

export class replica extends Program
{
	website  = "https://gondwanaland.com/meta/history/";
	unsafe   = true;
	loc      = "win7";
	bin      = "c:\\REPLICA\\REPLICA.EXE";
	args     = r => [r.inFile()];
	osData   = ({
		script   : `
			$mainWindow = WindowRequire("[CLASS:DPMDIFrameClass]", "", 20)

			Func PreOpenWindows()
				WindowFailure("Replica", "not a Replica document", -1, "{ENTER}")
			EndFunc
			CallUntil("PreOpenWindows", ${xu.SECOND*3})
		
			SendSlow("!fp")

			$printWindow = WindowRequire("Print", "", 7)
			Send("{ENTER}")

			HandleCutePDFPrint()

			WinWaitActive($mainWindow, "", 5)

			SendSlow("!fx")`
	});
	renameOut = true;
}
