import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class blpngConverter extends Program
{
	website   = "https://www.wowinterface.com/downloads/info22128-BLPNGConverter.html";
	loc       = "wine";
	bin       = "BLPNG Converter.exe";
	cwd       = r => r.outDir();
	exclusive = true;
	wineData  = r => ({
		base    : "win64",
		arch    : "win64",
		script  : `
			$mainWindow = WindowRequire("BLPNG Converter", "", 5)
			Send("{ALT}{RIGHT}{RIGHT}{DOWN}{ENTER}")
			$saveWindow = WindowRequire("", "File name:", 5)
			Send("c:\\in${r.wineCounter}\\${path.basename(r.inFile())}{ENTER}")
			WinWaitClose($saveWindow, "", 5)
			FileMove("c:\\in${r.wineCounter}\\${path.basename(r.inFile(), path.extname(r.inFile()))}.png", "c:\\out${r.wineCounter}\\${path.basename(r.inFile(), path.extname(r.inFile()))}.png")
			Send("{ALT}{DOWN}{DOWN}{DOWN}{ENTER}")
			WinWaitClose($mainWindow, "", 5)`
	});
	renameOut = true;
}


