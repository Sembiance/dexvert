import {xu} from "xu";
import {Program} from "../../Program.js";

export class totalCommander extends Program
{
	website = "https://totalcmd.net/plugring/totalcmd.html";
	loc     = "win2k";
	bin     = "c:\\Program Files\\totalcmd\\TOTALCMD.EXE";
	args    = r => [r.inFile(), "c:\\out", "/A"];
	notes   = "Has the plugin: https://totalcmd.net/plugring/resextract.html";
	osData  = ({
		script : `
			$mainWindow = WindowRequire("Total Commander 11.02 - ", "", 10)
			Sleep(500)
			Send("!{F9}")
			$unpackWindow = WindowRequire("Unpack files", "", 10)
			Send("{ENTER}")
			WinWaitClose($unpackWindow, "", 15)
			WinWaitActive($mainWindow, "", 60)
			Send("!f")
			Sleep(250)
			Send("q")`
	});
	renameOut = false;
}
