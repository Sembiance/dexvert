import {xu} from "xu";
import {Program} from "../../Program.js";

export class xRes extends Program
{
	loc      = "win2k";
	bin      = "c:\\Program Files\\Macromedia\\xRes3\\XRES3.EXE";
	args     = r => [r.inFile()];
	osData   = ({
		script : `
			$mainWindow = WindowRequire("Macromedia xRes", "", 10)
			MouseClick("left", 14, 28, 1, 0)
			Sleep(200)
			SendSlow("en")

			$saveWindow = WindowRequire("Save Image", "", 10)
			Send("c:\\out\\out.png{ENTER}")
			WinWaitClose($saveWindow, "", 10)

			$pngOptionsWindow = WindowRequire("PNG Options", "", 10)
			SendSlow("{UP}{UP}{ENTER}")
			WinWaitClose($pngOptionsWindow, "", 10)

			$progressWindow = WinWaitActive("[CLASS:MeterClass]", "Writing File", 3)
			If $progressWindow Then
				WinWaitClose($progressWindow, "", 180)
			EndIf

			WaitForStableFileSize("c:\\out\\out.png", ${xu.SECOND*2}, ${xu.MINUTE*3})`
	});
	renameOut = true;
}
