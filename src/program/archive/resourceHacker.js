import {xu} from "xu";
import {Program} from "../../Program.js";

export class resourceHacker extends Program
{
	website  = "http://www.angusj.com/resourcehacker/";
	loc      = "winxp";
	bin      = "c:\\dexvert\\resource_hacker\\ResourceHacker.exe";
	args     = r => [r.inFile()];
	qemuData = ({
		script : `
			WinWaitActive("Resource Hacker", "", 10)

			Send("!a")
			Sleep(250)
			Send("{DOWN}{DOWN}{DOWN}{DOWN}{DOWN}{DOWN}{DOWN}{ENTER}")

			WinWaitActive("Save resources to", "", 10)

			Send("c:\\out\\out.rc{ENTER}")

			WinWaitClose("Save resources to", "", 10)

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