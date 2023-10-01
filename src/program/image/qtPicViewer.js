import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class qtPicViewer extends Program
{
	website  = "https://github.com/Sembiance/dexvert/tree/master/os/aux/winxp/app/quicktimeplayer412.zip";
	unsafe   = true;
	loc      = "winxp";
	bin      = "C:\\Program Files\\QuickTime\\PictureViewer.exe";
	args     = r => [r.inFile()];
	osData   = r => ({
		script   : `
			$mainWindow = WindowRequire("${path.basename(r.inFile())}", "", 10)

			Send("^e")
			$saveImageWindow = WindowRequire("Save Image as:", "":, 10)
			Send("c:\\out\\out.png{ENTER}")
			WinWaitClose($saveImageWindow, "", 10)
			SendSlow("!fx")`});
	renameOut = true;
}
