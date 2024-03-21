import {xu} from "xu";
import {Program} from "../../Program.js";

export class goldBoxExplorer extends Program
{
	website   = "https://github.com/simeonpilgrim/goldboxexplorer";
	loc       = "win7";
	bin       = "c:\\dexvert\\gbexplorer-1.2\\gbexplorer.exe";
	args      = () => [];
	osData  = {
		script : `
			$mainWindow = WindowRequire("Gold Box Explorer", "", 15)
			Send("i{TAB}{TAB}{TAB}{END}")
			Sleep(1500)
			Send("+{F10}")
			Sleep(200)
			Send("E")

			$exportWindow = WindowRequire("Export Image", "", 15)
			$exportWindowPos = WinGetPos($exportWindow)
			MouseClick("left", $exportWindowPos[0] + 59, $exportWindowPos[1] + 59, 1, 0)

			$browseWindow = WindowRequire("Browse For Folder", "", 15)
			Sleep(250)
			SendSlow("{TAB}{TAB}{HOME}d{LEFT}c{RIGHT}l{RIGHT}o{ENTER}", 150)
			WinWaitClose($browseWindow, 10)

			WinWaitActive($exportWindow, "", 15)
			SendSlow("{TAB}{DOWN}{DOWN}{TAB}{TAB}{ENTER}")
			WindowRequire("", "Exported ", 120)
			Send("{ENTER}")`
	};

	renameOut      = {
		alwaysRename : true,
		regex        : /IN.DAX_(?<rest>.+)$/,
		renamer      :
		[
			(ignored, {rest}) => [rest]
		]
	};
}
