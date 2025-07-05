import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class konvertor extends Program
{
	website = "https://www.logipole.com/konvertor-en.htm";
	loc     = "win7";
	bin     = "c:\\Program Files (x86)\\Konvertor\\KonvertorFM.exe";
	args    = () => [];
	osData  = r => ({
		script : `
			FileDelete("c:\\in\\go.au3");
			WindowRequire("Konvertor - Computer", "", 10)
			SendSlow("{RIGHT}{ENTER}")
			WindowRequire("Konvertor - C:\\", "", 5)
			SendSlow("in{ENTER}")
			WindowRequire("Konvertor - C:\\in", "", 5)
			Sleep(250)
			MouseClick("right", 335, 277)
			Sleep(250)
			Send("{DOWN}{DOWN}{DOWN}{ENTER}")
			$convertWindow = WindowRequire("Konvertor - Convert Images", "", 7)
			Send("{ENTER}")
			WaitForStableFileSize("c:\\out\\${path.basename(r.inFile(), path.extname(r.inFile()))}.png", ${xu.SECOND*2}, ${xu.SECOND*15})
			Send("{ENTER}")
			WinWaitClose($convertWindow, "", 10)
			Send("!f")
			Send("{DOWN}{DOWN}{DOWN}{ENTER}")`
	});
	renameOut = true;
}
