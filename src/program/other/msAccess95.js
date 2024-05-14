import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class msAccess95 extends Program
{
	website = "https://winworldpc.com/product/microsoft-access/95";
	loc     = "win2k";
	bin     = "c:\\MSOffice\\Access\\MSACCESS.EXE";
	osData  = r => ({
		script : `
			$choiceWindow = WindowRequire("Microsoft Access", "Open an Existing Database", 7)
			SendSlow("o{ENTER}")
			$openWindow = WindowRequire("Open", "", 5)
			Send("c:\\in\\${path.basename(r.inFile())}{ENTER}")
			$convertWindow = WindowRequire("Convert/Open Database", "Convert Database", 10)
			SendSlow("c{ENTER}")
			$saveWindow = WindowRequire("Convert Database Into", "", 5)
			Send("c:\\out\\out.mdb{ENTER}")
			WinWaitClose($saveWindow, "", 20)
			WaitForStableFileSize("c:\\out\\out.mdb", ${xu.SECOND*3}, ${xu.SECOND*30})
			SendSlow("!fx")`
	});
	renameOut = true;
}
