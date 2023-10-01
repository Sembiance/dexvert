import {xu} from "xu";
import {Program} from "../../Program.js";

export class resourceEditor extends Program
{
	website  = "http://melander.dk/reseditor/";
	loc      = "winxp";
	bin      = "c:\\dexvert\\ResourceEditor\\ResourceEditor.exe";
	notes    = "Not currently working, doesn't launch in the 86Box emulated Windowx XP, no idea why.";
	args     = r => [r.inFile()];
	osData   = ({
		script : `
			WinWaitActive("Resource Editor", "", 10)

			AutoItSetOption("SendKeyDelay", 20)

			SendSlow("!f")
			Sleep(250)
			Send("{DOWN}{DOWN}{DOWN}{DOWN}{ENTER}")

			WinWaitActive("Save resource file", "", 10)

			Sleep(250)

			Send("{TAB}{DOWN}{DOWN}{DOWN}{DOWN}{ENTER}")
			Sleep(100)
			Send("+{TAB}c:\\out\\out.rc{TAB}{TAB}{TAB}{TAB}{DOWN}{ENTER}")

			WinWaitClose("Save resource file", "", 10)

			Sleep(200)
			
			SendSlow("!fx", 250)`
	});
	renameOut = {
		alwaysRename : true,
		renamer      : [({fn, originalInput}) => (originalInput && fn==="out.rc" ? [originalInput.name, ".rc"] : [fn])]
	};
}
