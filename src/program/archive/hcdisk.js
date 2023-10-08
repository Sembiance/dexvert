import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class hcdisk extends Program
{
	website   = "https://github.com/0sAND1s/HCDisk";
	loc       = "wine";
	bin       = "HCDisk2.exe";
	cwd       = r => r.outDir();
	exclusive = "wine";
	wineData  = r => ({
		console : true,
		script  : `
			$mainWindow = WindowRequire("c:\\dexvert\\HCDisk2.exe", "", 5)
			Sleep(1000)
			Send("open c:\\in${r.wineCounter}\\${path.basename(r.inFile())}{ENTER}")
			Sleep(1000)
			Send("get *{ENTER}")
			Sleep(1000)
			Send("exit{ENTER}")
			WinWaitClose($mainWindow, "", 5)`
	});
	renameOut = false;
}
