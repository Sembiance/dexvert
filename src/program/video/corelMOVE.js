import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class corelMOVE extends Program
{
	website  = "https://winworldpc.com/product/corel-draw/50";
	loc      = "win2k";
	bin      = "c:\\COREL50\\PROGRAMS\\CORELMOV.EXE";
	//args     = r => [r.inFile()];
	osData   = r => ({
		alsoKill : ["ntvdm.exe"],
		script   : `
			$mainWindow = WindowRequire("CorelMOVE", "", 10)
			
			Send("^o")
			$openWindow = WindowRequire("Open Animation File", "", 5);
			Send("c:\\in\\${path.basename(r.inFile())}{ENTER}")
			WinWaitClose($openWindow);

			WinWaitActive($mainWindow, "", 3)

			SendSlow("!fem")
			WindowRequire("Export To Movie", "", 5)
			Send("c:\\out\\out.avi{ENTER}")
			WindowRequire("Compression Method", "", 5)
			Send("{ENTER}");

			$exportWindow = WindowRequire("Exporting to Movie", "", 5)
			WinWaitClose($exportWindow, "", 30)
			WinWaitActive($mainWindow, "", 3)
			
			SendSlow("!fx")`
	});
	renameOut = true;
	chain     = `dexvert[asFormat:video/avi]`;
}
