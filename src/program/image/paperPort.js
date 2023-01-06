import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class paperPort extends Program
{
	website  = "https://archive.org/details/PaperPort_Deluxe_6.1_Windows_1999";
	loc      = "win2k";
	bin      = "c:\\Program Files\\Visioneer\\PaperPort\\Paprport.exe";
	qemuData = r => ({
		script   : `
			$mainWindow = WindowRequire("Visioneer PaperPort", "", 10)
			SendSlow("!fi")
			$importWindow = WindowRequire("Import", "", 5)
			Send("c:\\in\\${path.basename(r.inFile())}{ENTER}")
			WinWaitClose($importWindow, "", 10)
			WinWaitActive($mainWindow, "", 5)

			SendSlow("!fe")

			$exportWindow = WindowRequire("Export", "", 5)
			Send("c:\\out\\out.png{TAB}{DOWN}{END}{UP}{ENTER}{ENTER}")
			WinWaitClose($exportWindow, "", 10)

			WinWaitActive($mainWindow, "", 10)

			Send("{DELETE}")	; Importing the file copies it over to some working directory, so let's delete it
			Sleep(1000)
			
			SendSlow("!fx")
			
			FileRecycleEmpty()	; Deleting the imported file above only moves it to the recycle bin, so let's empty it`
	});
	renameOut = true;
}
