import {xu} from "xu";
import {Program} from "../../Program.js";

export class xRes extends Program
{
	loc      = "win7";
	bin      = "c:\\Program Files\\Macromedia\\xRes3\\XRES3.EXE";
	args     = r => [r.inFile()];
	osData   = ({
		script : `
			$mainWindow = WindowRequire("Macromedia xRes", "", 15)
			Sleep(1000)
			MouseClick("left", 14, 28, 1, 0)
			Sleep(1000)
			SendSlow("en")

			$saveWindow = WindowRequire("Save Image", "", 15)
			SendSlow("{DOWN}{UP}{ENTER}{TAB}{TAB}out{ENTER}{TAB}out.png{ENTER}")
			WinWaitClose($saveWindow, "", 15)

			$pngOptionsWindow = WindowRequire("PNG Options", "", 15)
			SendSlow("{UP}{UP}{ENTER}")
			WinWaitClose($pngOptionsWindow, "", 15)

			WaitForStableFileSize("c:\\out\\out.png", ${xu.SECOND*4}, ${xu.MINUTE*2.5})`
	});
	renameOut = true;
}
