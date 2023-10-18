import {xu} from "xu";
import {Program} from "../../Program.js";

export class quickTimePlayer extends Program
{
	website  = "https://github.com/Sembiance/dexvert/tree/master/os/aux/winxp/app/quicktimeplayer412.zip";
	unsafe   = true;
	loc      = "winxp";
	bin      = "C:\\Program Files\\QuickTime\\QuickTimePlayer.exe";
	args     = r => [r.inFile()];
	osData   = {
		script   : `
			$mainWindow = WindowRequire("QuickTimePlayer", "", 10);
			Sleep(5000)
			SendSlow("!fa")
			$saveWindow = WindowRequire("Save As", "", 5)
			Send("c:\\out\\out.avi")
			SendSlow("{TAB}{TAB}{TAB}{TAB}{UP}{ENTER}");
			WinWaitClose($saveWindow, "", 10)
			SendSlow("!fx")
			WinWaitClose($mainWindow, "", 10)`};
	renameOut = true;
	chain     = "ffmpeg";
}
