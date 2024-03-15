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
			$mainWindow = WindowRequire("Gold Box Explorer", "", 10)
			Send("i{TAB}{TAB}{TAB}{END}")
			Sleep(1000)
			Send("+{F10}")
			Send("E")

			$exportWindow = WindowRequire("Export Image", "", 10)
			$exportWindowPos = WinGetPos($exportWindow)
			MouseClick("left", $exportWindowPos[0] + 59, $exportWindowPos[1] + 59, 1, 0)

			$browseWindow = WindowRequire("Browse For Folder", "", 10)
			Sleep(200)
			SendSlow("{TAB}{TAB}{HOME}d{LEFT}c{RIGHT}l{RIGHT}o{ENTER}", 100)
			WinWaitClose($browseWindow, 10)

			WinWaitActive($exportWindow, "", 10)
			SendSlow("{TAB}{DOWN}{DOWN}{TAB}{TAB}{ENTER}")
			WindowRequire("", "Exported ", 60)
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
