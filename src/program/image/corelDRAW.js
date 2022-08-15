import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class corelDRAW extends Program
{
	website  = "https://winworldpc.com/product/corel-draw/50";
	loc      = "win2k";
	bin      = "c:\\COREL50\\PROGRAMS\\CORELDRW.EXE";
	qemuData = r => ({
		alsoKill : ["ntvdm.exe"],
		script   : `
			$mainWindow = WindowRequire("CorelDRAW", "", 10)

			Send("!fi")
			$importWindow = WindowRequire("Import", "", 5)
			Send("c:\\in\\${path.basename(r.inFile())}{ENTER}")
			WinWaitClose($importWindow, "", 0)

			Func PostImportWindows()
				WindowFailure("Filter Error", "", -1, "{ENTER}")
				WindowFailure("CorelDRAW!", "Error Reading", -1, "{ENTER}")
				WindowFailure("Application Error", "", -1, "{ENTER}")
				WindowDismiss("Photo CD Options", "", "{TAB}{TAB}{TAB}{TAB}{ENTER}")
				WindowDismiss("PANOSE Font Matching Results", "", "{ENTER}")
			EndFunc
			CallUntil("PostImportWindows", ${xu.SECOND*3})

			WinWaitActive($mainWindow, "", 10)

			Send("!fe")

			WindowRequire("Export", "", 5)
			Send("c:\\out\\out.bmp{TAB}{TAB}{TAB}{HOME}w{ENTER}")
			$bitmapWindow = WindowRequire("Bitmap Export", "", 5)
			WindowDismissWait("Bitmap Export", "", 5, "{ENTER}")

			WinWaitClose("CorelDRAW! is Exporting...", "", 10)

			WinWaitActive($mainWindow, "", 3)

			Send("!f")
			Sleep(200)
			Send("x")
			
			WindowDismissWait("CorelDRAW!", "Save current changes", 3, "n")`
	});
	renameOut = true;
	chain     = "dexvert[asFormat:image/bmp]";
}
