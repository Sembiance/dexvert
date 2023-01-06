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
			SendSlow("!fg")

			WinWaitActive("Generate Font Files", "", 10)
			Sleep(100)
			Send("{ENTER}")
			WinWaitClose("Generate Font Files", "", 10)
			Sleep(500)

			SendSlow("!fx")`
	});
	renameOut = false;
}
