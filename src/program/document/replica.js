import {Program} from "../../Program.js";

export class replica extends Program
{
	website  = "https://gondwanaland.com/meta/history/";
	unsafe   = true;
	loc      = "win2k";
	bin      = "c:\\REPLICA\\REPLICA.EXE";
	args     = r => [r.inFile()];
	qemuData = ({
		script : `
			WinWaitActive("[CLASS:DPMDIFrameClass]", "", 20)
		
			Sleep(200)
			Send("!f")
			Sleep(200)
			Send("a")

			WinWaitActive("[TITLE:Save As]", "", 10)

			Sleep(200)
			Send("c:\\out\\out.txt{TAB}{TAB}{TAB}t{ENTER}")
			
			WinWaitClose("[TITLE:Save As]", "", 10)
			Sleep(200)

			Sleep(200)
			Send("!f")
			Sleep(200)
			Send("x")
			
			WinWaitClose("[CLASS:DPMDIFrameClass]", "", 10)`
	});
	renameOut = true;
}
