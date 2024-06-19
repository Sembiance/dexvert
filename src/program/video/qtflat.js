import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";
import {fileUtil} from "xutil";

export class qtflat extends Program
{
	website       = "https://samples.mplayerhq.hu/V-codecs/601P/";
	loc           = "wine";
	checkForDups  = true;
	bin           = "c:\\dexvert\\qtflat\\QT-Flattener.exe";
	mirrorInToCWD = "copy";
	cwd           = r => r.outDir();
	exclusive     = "wine";
	wineData      = () => ({
		script  : `
			$mainWindow = WindowRequire("QT-Flattener", "", 10)
			Sleep(2000)
			SendSlow("{TAB}{RIGHT}")
			Sleep(1000)
			SendSlow("{TAB}{TAB}{TAB}{TAB}{TAB}{TAB}{TAB}")
			SendSlow("{ENTER}")
			Sleep(4000)
			SendSlow("+{TAB}{ENTER}")
			WinWaitClose($mainWindow, "", 20)`
	});
	postExec = async r =>
	{
		const outputOldFilePath = path.join(r.outDir({absolute : true}), path.basename(r.inFile()));
		if(!await fileUtil.exists(outputOldFilePath))
			return;

		await Deno.rename(outputOldFilePath, path.join(r.outDir({absolute : true}), "out.mov"));
	};
	chain     = "dexvert";
	renameOut = true;
}
