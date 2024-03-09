import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class Crowbar extends Program
{
	website   = "https://github.com/ZeqMacaw/Crowbar";
	loc       = "wine";
	bin       = "Crowbar.exe";
	exclusive = "wine";
	args      = r => [`c:\\in${r.wineCounter}\\${path.basename(r.inFile())}`];
	wineData  = r => ({
		script : `
			$mainWindow = WindowRequire("Crowbar", "", 10)
			DirRemove("c:\\dexvert\\aacrow", 1)
			DirCreate("c:\\dexvert\\aacrow")
			ControlClick($mainWindow, "", "[NAME:BrowseForOutputPathButton]")
			$browseWindow = WindowRequire("Open the folder you want as Output Folder", "", 5)
			Sleep(300)
			MouseClick("left", 324, 180, 2, 0)
			ControlClick($browseWindow, "", "[CLASS:Button; TEXT:&Open]")
			WinWaitClose($browseWindow, 5)
			WinWaitActive($mainWindow, "", 10)
			ControlClick($mainWindow, "", "[NAME:DecompileButton]")
			Sleep(200)
			Func WaitForDecompileToFinish()
				return StringRegExp(ControlGetText($mainWindow, "", "[NAME:DecompilerLogTextBox]"), 'finished\\.\\s*$', 0)
			EndFunc
			CallUntil("WaitForDecompileToFinish", ${xu.MINUTE})
			Sleep(200)
			DirRemove("c:\\out${r.wineCounter}\\", 1)
			DirMove("c:\\dexvert\\aacrow", "c:\\out${r.wineCounter}")`
	});

	renameOut = false;
}
