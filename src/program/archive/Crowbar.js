import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class Crowbar extends Program
{
	website   = "https://github.com/ZeqMacaw/Crowbar";
	loc       = "win7";
	bin       = "Crowbar.exe";
	args      = r => [`c:\\in\\${path.basename(r.inFile())}`];
	osData  = {
		script : `
			$mainWindow = WindowRequire("Crowbar", "", 10)
			ControlClick($mainWindow, "", "[NAME:BrowseForOutputPathButton]")
			$browseWindow = WindowRequire("Open the folder you want as Output Folder", "", 10)
			Sleep(300)
			Send("c:\\out{ENTER}")
			Sleep(1500)
			Send("{ENTER}")
			WinWaitClose($browseWindow, 10)
			WinWaitActive($mainWindow, "", 10)
			ControlClick($mainWindow, "", "[NAME:DecompileButton]")

			Sleep(200)
			Func WaitForDecompileToFinish()
				return StringRegExp(ControlGetText($mainWindow, "", "[NAME:DecompilerLogTextBox]"), 'finished\\.\\s*$', 0)
			EndFunc
			CallUntil("WaitForDecompileToFinish", ${xu.MINUTE})`
	};

	renameOut = false;
}
