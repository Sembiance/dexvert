import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class resourceEditor extends Program
{
	website  = "http://melander.dk/reseditor/";
	loc      = "wine";
	bin      = "c:\\dexvert\\ResourceEditor\\ResourceEditor.exe";
	args     = r => [r.inFile()];
	notes    = "This broke in 86Box. It's flaky in wine too, program doesn't seem to be able to export anything without errors. Blegh. So currently nothing is using this";
	wineData = r => ({
		script : `
			AutoItSetOption("SendKeyDelay", 20)
			$mainWindow = WindowRequire("Resource Editor", "", 10)
			
			; Sometimes the main window appears early but isn't ready for keyboard interaction yet
			Sleep(2000)

			Func OpenSaveWindow()
				SendSlow("!f")
				Sleep(200)
				Send("{DOWN}{DOWN}{DOWN}{DOWN}{ENTER}")
				Sleep(2000)
			EndFunc

			Func PerformSaving($saveWindow)
				Sleep(500)
				
				$dupFileWindow = WinActive("Save resource file", "Do you want to replace it?")
				If $dupFileWindow Not = 0 Then
					Send("{ESCAPE}")
					WinWaitClose($dupFileWindow, "", 2)
					FileDelete("c:\\${path.basename(r.inFile())}")
					WinWaitActive($saveWindow, "", 2)
				EndIf

				Send("{TAB}{DOWN}{DOWN}{DOWN}+{TAB}c:\\out${r.wineCounter}\\out.rc{TAB}{TAB}{TAB}{TAB}{TAB}{DOWN}{ENTER}")
				WinWaitClose($saveWindow, "", 10)
			EndFunc

			OpenSaveWindow()
			$saveResourceWindow = WinWaitActive("Save resource file", "", 3)
			If $saveResourceWindow Then
				PerformSaving($saveResourceWindow)
			Else
				OpenSaveWindow()
				$saveResourceWindow = WindowRequire("Save resource file", "", 3)
				PerformSaving($saveResourceWindow)
			EndIf

			Sleep(500)
			
			SendSlow("!fx", 250)`
	});
	renameOut = {
		alwaysRename : true,
		renamer      : [({fn, originalInput}) => (originalInput && fn==="out.rc" ? [originalInput.name, ".rc"] : [fn])]
	};
}
