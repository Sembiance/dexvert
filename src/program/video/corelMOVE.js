import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class corelMOVE extends Program
{
	website  = "https://winworldpc.com/product/corel-draw/50";
	loc      = "win2k";
	bin      = "c:\\COREL50\\PROGRAMS\\CORELMOV.EXE";
	args     = r => [r.inFile()];
	osData   = r => ({
		alsoKill : ["ntvdm.exe"],
		script   : `
			$mainWindow = WindowRequire("CorelMOVE - ${path.basename(r.inFile()).toUpperCase()}", "", 10)
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
