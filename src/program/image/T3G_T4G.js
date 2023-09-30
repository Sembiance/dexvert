import {Program} from "../../Program.js";

export class T3G_T4G extends Program
{
	website  = "https://archive.org/details/t425l1e_zip";
	unsafe   = true;
	loc      = "win2k";
	bin      = "c:\\tscad4\\T3G_T4G.EXE";
	args     = r => [r.inFile()];
	osData   = ({
		script : `
			$mainWindow = WindowRequire("[CLASS:ConvertWClass]", "", 5)

			Send("{F2}")

			$selectSourceWindow = WindowRequire("[TITLE:Select source file]", "", 10)
			Send("c:\\in{ENTER}")
			Sleep(200)
			Send("{TAB}{DOWN}{ENTER}")
			WinWaitClose($selectSourceWindow, "", 10)

			$selectTargetWindow = WindowRequire("[TITLE:Select target file]", "", 10)
			Send("c:\\out{ENTER}")
			Sleep(200)
			Send("out.t4g{ENTER}")
			WinWaitClose($selectTargetWindow, "", 10)

			WinWaitActive($mainWindow, "", 10)
			SendSlow("!fx")`});
	renameOut = true;
	chain     = "CADDraw";
}
