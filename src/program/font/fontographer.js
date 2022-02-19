import {Program} from "../../Program.js";

export class fontographer extends Program
{
	website  = "https://www.fontlab.com/font-editor/fontographer/";
	loc      = "winxp";
	bin      = "c:\\Program Files\\Fontlab\\Fontographer 5\\Fontographer 5.exe";
	args     = r => [r.inFile()];
	qemuData = ({
		script : `
			WinWaitActive("Fontographer 5.2", "", 10)
			Sleep(500)
			Send("!f")
			Sleep(100)
			Send("g")
			Sleep(100)

			WinWaitActive("Generate Font Files", "", 10)
			Sleep(100)
			Send("{ENTER}")
			WinWaitClose("Generate Font Files", "", 10)
			Sleep(500)

			Send("!f")
			Sleep(100)
			Send("x")
			Sleep(100)`
	});
	renameOut = false;
}
