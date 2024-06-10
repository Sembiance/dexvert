import {xu} from "xu";
import {Program} from "../../Program.js";

export class neoDraw extends Program
{
	website  = "https://archive.org/details/twilight-dvd069";
	unsafe   = true;
	loc      = "win2k";
	bin      = "c:\\dexvert\\NEODRAW\\NEODRAW.EXE";
	args     = r => [r.inFile()];
	osData   = ({
		script : `
			WindowDismissWait("Welcome to NeoDraw", "", 5, "{ENTER}")
			WindowDismissWait("About NeoDraw", "", 5, "{ENTER}")

			Func MainWindowOrFailure()
				WindowFailure("NeoDraw", "Unable to open", -1, "{ENTER}")
				return WinActive("NeoDraw - ", "")
			EndFunc
			$mainWindow = CallUntil("MainWindowOrFailure", ${xu.SECOND*10})

			Send("!f")
			Send("em")

			$exportWindow = WindowRequire("Save As", "", 10)
			Send("c:\\out\\out.wmf{ENTER}")
			WinWaitClose($exportWindow, "", 10)

			WaitForStableFileSize("c:\\out\\out.wmf", ${xu.SECOND*3}, ${xu.SECOND*15})

			Send("!f")
			Send("x")

			WinWaitClose($mainWindow, "", 5)`});
	renameOut = true;
	chain     = "dexvert[asFormat:image/wmf]";
}
