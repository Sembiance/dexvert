import {xu} from "xu";
import {Program} from "../../Program.js";

export class winPack extends Program
{
	website  = "https://web.archive.org/web/20060210083422/http://snoopy81.ifrance.com/snoopy81/en/winpack.htm";
	unsafe   = true;
	loc      = "winxp";
	bin      = "c:\\dexvert\\WinPack300b\\WinPack.exe";
	args     = r => [r.inFile()];
	osData   = ({
		dontMaximize : true,
		script : `
			$mainWindow = WindowRequire("[TITLE:WinPack; CLASS:TisMainForm]", "", 10)
			Sleep(250)
			SendSlow("!fu")

			$browseWindow = WindowRequire("[TITLE:Browse for Folder]", "", 10)
			Sleep(250)
			SendSlow("{PGUP}{PGUP}{PGUP}{DOWN}{DOWN}{DOWN}{DOWN}{RIGHT}out{ENTER}")
			WinWaitClose($browseWindow, "", 15)
			Sleep(1000)

			SendSlow("!fx")

			WaitForPID("WinPack.exe", ${xu.SECOND*10})`
	});
	renameOut = false;
}
