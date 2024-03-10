import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class cinema4D427 extends Program
{
	website = "https://archive.org/details/maxoncinema4dr4.27.7z";
	loc     = "win2k";
	bin     = "c:\\dexvert\\Cinema 4D R4.27\\Cinema4D.exe";
	args    = r => [r.inFile()];
	osData  = r => ({
		script : `
			Func MainWindowOrFailure()
				WindowFailure("CINEMA 4D - Message", "Unknown file format", -1, "{ESCAPE}")
				return WinActive("CINEMA 4D - [${path.basename(r.inFile())}]", "")
			EndFunc
			$mainWindow = CallUntil("MainWindowOrFailure", ${xu.SECOND*10})
			Sleep(1000)

			Send("!f")
			Send("{DOWN}{DOWN}{DOWN}{DOWN}{DOWN}{RIGHT}{UP}{ENTER}")

			Func WaitForSaveWindow()
				WindowDismiss("CINEMA 4D", "Please select an object", "{ENTER}")
				return WinActive("Save file", "")
			EndFunc
			$saveWindow = CallUntil("WaitForSaveWindow", ${xu.SECOND*10})
			Send("c:\\out\\out.q3d{ENTER}")
			WinWaitClose($saveWindow, "", 10)
			WaitForStableFileSize("c:\\out\\out.q3d", ${xu.SECOND*3}, ${xu.SECOND*30})` });
	renameOut = true;
	chain     = "dexvert[asFormat:poly/quickDraw3D]";
}
