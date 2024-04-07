import {Program} from "../../Program.js";

export class T2G_T3G extends Program
{
	website  = "https://archive.org/details/t425l1e_zip";
	unsafe   = true;
	loc      = "win2k";
	bin      = "c:\\tscad4\\T2G_T3G.EXE";
	osData   = ({
		script : `
			$mainWindow = WindowRequire("[CLASS:ConvertWClass]", "", 5)

			Send("{F2}")

			; There is no keyboard control of the menus here, so we have to determine how many folders before in/out and click on the proper pixel
			Local $cDirs = ListCDirs()

			$selectSourceWindow = WindowRequire("[TITLE:Select source file]", "", 10)
			MouseClick("left", 490, 331+((_ArraySearch($cDirs, "in")-1)*16), 2, 0)
			MouseClick("left", 298, 331, 2, 0)
			WinWaitClose("[TITLE:Select source file]", "", 10)

			$selectTargetWindow = WindowRequire("[TITLE:Select target file]", "", 10)
			MouseClick("left", 490, 331+((_ArraySearch($cDirs, "out")-1)*16), 2, 0)
			Send("out.t3g{ENTER}")
			WinWaitClose($selectTargetWindow, "", 10)

			WinWaitActive($mainWindow, "", 10)
			SendSlow("!fx")`});
	renameOut = true;
	chain     = "T3G_T4G";
}
