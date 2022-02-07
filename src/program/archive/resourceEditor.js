import {xu} from "xu";
import {Program} from "../../Program.js";

export class resourceEditor extends Program
{
	website  = "http://melander.dk/reseditor/";
	loc      = "winxp";
	bin      = "c:\\dexvert\\ResourceEditor\\ResourceEditor.exe";
	args     = r => [r.inFile()];
	qemuData = ({
		script : `
			WinWaitActive("Resource Editor", "", 10)

			AutoItSetOption("SendKeyDelay", 20)

			Send("!f")
			Sleep(250)
			Send("{DOWN}{DOWN}{DOWN}{DOWN}{ENTER}")

			WinWaitActive("Save resource file", "", 10)

			Sleep(250)

			Send("{TAB}{DOWN}{DOWN}{DOWN}{DOWN}{ENTER}")
			Sleep(100)
			Send("+{TAB}c:\\out\\out.rc{TAB}{TAB}{TAB}{TAB}{DOWN}{ENTER}")

			WinWaitClose("Save resource file", "", 10)

			Sleep(200)
			
			Send("!f")
			Sleep(250)
			Send("x")`
	});
	renameOut = {
		alwaysRename : true,
		renamer      : [({fn, originalInput}) => (originalInput && fn==="out.rc" ? [originalInput.name, ".rc"] : [fn])]
	};
}
