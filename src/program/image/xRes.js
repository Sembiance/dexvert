import {xu} from "xu";
import {Program} from "../../Program.js";

export class xRes extends Program
{
	loc      = "win7";
	bin      = "c:\\Program Files\\Macromedia\\xRes3\\XRES3.EXE";
	args     = r => [r.inFile()];
	osData   = ({
		script : `
			$mainWindow = WindowRequire("Macromedia xRes", "", 10)
			Sleep(1000)
			MouseClick("left", 14, 28, 1, 0)
			Sleep(500)
			SendSlow("en")

			$saveWindow = WindowRequire("Save Image", "", 10)
			Send("{TAB}{TAB}{TAB}{TAB}c:\\out\\out.png{ENTER}")
			WinWaitClose($saveWindow, "", 10)

			$pngOptionsWindow = WindowRequire("PNG Options", "", 10)
			SendSlow("{UP}{UP}{ENTER}")
			WinWaitClose($pngOptionsWindow, "", 10)

			WaitForStableFileSize("c:\\out\\out.png", ${xu.SECOND*3}, ${xu.MINUTE*2})`
	});
	renameOut = true;
}
