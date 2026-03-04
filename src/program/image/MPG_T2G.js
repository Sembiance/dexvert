import {Program} from "../../Program.js";

export class MPG_T2G extends Program
{
	website  = "https://archive.org/details/t425l1e_zip";
	unsafe   = true;
	loc      = "win7";
	bin      = "c:\\tscad4\\MPG_T2G.EXE";
	osData   = ({
		script : `
			$mainWindow = WindowRequire("[CLASS:ConvertWClass]", "", 5)

			Send("{F2}")

			$selectSourceWindow = WindowRequire("[TITLE:Select source file]", "", 10)
			MouseClick("left", 490, 445, 1, 0)
			MouseClick("left", 324, 331, 2, 0)
			WinWaitClose("[TITLE:Select source file]", "", 10)

			$selectTargetWindow = WindowRequire("[TITLE:Select target file]", "", 10)
			MouseClick("left", 490, 523, 1, 0)
			Send("out.t2g{ENTER}")
			WinWaitClose($selectTargetWindow, "", 10)

			WinWaitActive($mainWindow, "", 10)
			SendSlow("!fx")`});
	renameOut = true;
	chain     = "T2G_T3G";
}
