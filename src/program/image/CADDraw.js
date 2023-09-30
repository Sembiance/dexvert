import {Program} from "../../Program.js";

export class CADDraw extends Program
{
	website  = "https://archive.org/details/t425l1e_zip";
	unsafe   = true;
	loc      = "win2k";
	bin      = "c:\\tscad4\\RELEASE4.EXE";
	args     = r => [r.inFile()];
	osData   = ({
		script : `
			$mainWindow = WindowRequire("[CLASS:MainWClassToso4]", "", 10)

			Sleep(500)
			SendSlow("!fa")

			$exportWindow = WindowRequire("[TITLE:Save Drawing as...]", "", 10)
			Send("c:\\out\\out.wmf{TAB}w{ENTER}")
			WinWaitClose("Save Drawing as...", "", 10)

			WindowDismissWait("[TITLE:Message]", "", 10, "Y")
			WinWaitActive($mainWindow, "", 10)

			SendSlow("!fx")`});
	renameOut = true;
	chain     = "dexvert[asFormat:image/wmf]";
}
