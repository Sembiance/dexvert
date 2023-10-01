import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class hcdisk extends Program
{
	website  = "https://github.com/0sAND1s/HCDisk";
	loc      = "wine";
	bin      = "HCDisk2.exe";
	cwd      = r => r.outDir();
	wineData = r => ({
		console : true,
		script :
		[
			{ op : "windowRequire", matcher : /^c:\\dexvert\\HCDisk2.exe/, timeout : xu.SECOND*5, windowid : "mainWindow"},
			{ op : "delay", duration : xu.SECOND},
			{ op : "type", windowid : "mainWindow", text : `open C:\\in\\${path.basename(r.inFile())}{Return}` },
			{ op : "delay", duration : xu.SECOND},
			{ op : "type", windowid : "mainWindow", text : `get *{Return}` },
			{ op : "delay", duration : xu.SECOND},
			{ op : "type", windowid : "mainWindow", text : `exit{Return}` }
		]
	});
	renameOut = false;
}
