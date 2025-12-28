import {xu} from "xu";
import {Program} from "../../Program.js";

export class ultraISO extends Program
{
	website  = "https://www.ezbsystems.com/ultraiso/history.htm";
	loc      = "win7";
	bin      = "c:\\Program Files (x86)\\UltraISO\\UltraISO.exe";
	args     = r => [r.inFile()];
	osData   = () => ({
		script : `
			WindowRequire("UltraISO", "", 30)
			Sleep(5000)
			SendSlow("!fa")
			$saveAsWindow = WindowRequire("ISO File Save As", "", 15)
			Send("{DELETE}c:\\out\\out.iso{ENTER}")
			WinWaitClose($saveAsWindow, "", 180)
			WaitForStableFileSize("c:\\out\\out.iso", ${xu.SECOND*20}, ${xu.MINUTE*5})
			SendSlow("!fx")`
	});
	renameOut = true;
}
