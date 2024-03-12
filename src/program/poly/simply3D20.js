import {xu} from "xu";
import {Program} from "../../Program.js";

export class simply3D20 extends Program
{
	website   = "https://archive.org/details/premier2_cd";
	loc       = "win2k";
	bin       = "c:\\Program Files\\Micrografx\\Simply 3D 2\\S3D2.exe";
	args      = r => [r.inFile()];
	osData    = ({
		script : `
			$mainWindow = WindowRequire("Simply 3D - ", "", 15)
			Send("!f")
			Send("a")
			$saveWindow = WindowRequire("Save As", "", 10)
			Send("{TAB}{DOWN}{END}{ENTER}")
			Sleep(500)
			Send("c:\\out\\out.wrl{ENTER}")
			WinWaitClose($saveWindow, "", 10)
			$vrmlWindow = WindowRequire("VRML Export", "", 10)
			Send("{TAB}{TAB}{TAB}{END}")
			Sleep(250)
			Send("{ENTER}")
			WinWaitClose($vrmlWindow, "", 20)
			WaitForStableFileSize("c:\\out\\out.wrl", ${xu.SECOND*3}, ${xu.SECOND*30})`
	});
	renameOut = true;
	chain     = "dexvert[asFormat:poly/vrml]";
}
