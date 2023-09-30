import {Program} from "../../Program.js";

export class MPG_T2G extends Program
{
	website  = "https://archive.org/details/t425l1e_zip";
	unsafe   = true;
	loc      = "win2k";
	bin      = "c:\\tscad4\\MPG_T2G.EXE";
	osData   = ({
		script : `
			$mainWindow = WindowRequire("[CLASS:ConvertWClass]", "", 5)

			Send("{F2}")

			; There is no keyboard control of the menus here, so we have to determine how many folders before in/out and click on the proper pixel
			Local $cDirs = ListCDirs()

			$selectSourceWindow = WindowRequire("[TITLE:Select source file]", "", 10)
			MouseClick("left", 490, 331+((_ArraySearch($cDirs, "in")-1)*17), 1, 0)
			MouseClick("left", 324, 331, 2, 0)
			WinWaitClose("[TITLE:Select source file]", "", 10)

			$selectTargetWindow = WindowRequire("[TITLE:Select target file]", "", 10)
			MouseClick("left", 490, 331+((_ArraySearch($cDirs, "out")-1)*17), 1, 0)
			Send("out.t2g{ENTER}")
			WinWaitClose($selectTargetWindow, "", 10)

			WinWaitActive($mainWindow, "", 10)
			SendSlow("!fx")`});
	renameOut = true;
	chain     = "T2G_T3G";
}
