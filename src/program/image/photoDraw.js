import {xu} from "xu";
import {Program} from "../../Program.js";

export class photoDraw extends Program
{
	website  = "https://archive.org/details/PhotoDraw2000V2";
	loc      = "win2k";
	bin      = "c:\\Program Files\\Microsoft Office\\Office\\PHOTODRW.EXE";
	args     = () => [];
	osData   = ({
		script : `
			$mainWindow = WindowRequire("Microsoft PhotoDraw", "", 10)

			Send("!f")
			Sleep(2500)
			Send("h")

			WindowRequire("Batch Save Wizard: Select Batch Operation", "", 10)
			Send("pn")

			WindowRequire("Batch Save Wizard: Select a Folder of Pictures", "", 10)
			Send("n")

			WindowRequire("Batch Save Wizard: Save Options", "", 10)
			Send("w")
			$selectFolderWindow = WindowRequire("Select Folder", "", 5)
			Send("c:\\out{ENTER}")
			WinWaitClose($selectFolderWindow, "", 5)
			Send("s{END}{UP}{UP}{UP}{UP}{TAB}{TAB}{TAB}{TAB}n")

			WindowRequire("Batch Save Wizard: Sizing Options", "", 10)
			Send("of")

			Func PostSaveWindows()
				$saveProgressWindow = WinActive("Batch Save Wizard: Saving Pictures", "")
				If $saveProgressWindow Not = 0 Then
					WinWaitClose($saveProgressWindow, "", 120)	; can take some time to output the result
				EndIf
				return WindowDismiss("Batch Save Wizard: Finished", "", "{ENTER}")
			EndFunc
			CallUntil("PostSaveWindows", ${xu.SECOND*15})	; this gives it 15 seconds to start saving`
	});
	renameOut = true;
}
