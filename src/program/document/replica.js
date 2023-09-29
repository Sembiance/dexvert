import {Program} from "../../Program.js";

export class replica extends Program
{
	website  = "https://gondwanaland.com/meta/history/";
	unsafe   = true;
	loc      = "win2k";
	bin      = "c:\\REPLICA\\REPLICA.EXE";
	args     = r => [r.inFile()];
	osData   = ({
		script : `
			WinWaitActive("[CLASS:DPMDIFrameClass]", "", 20)
		
			SendSlow("!fa")

			WinWaitActive("[TITLE:Save As]", "", 10)

			Sleep(200)
			Send("c:\\out\\out.txt{TAB}{TAB}{TAB}t{ENTER}")
			
			WinWaitClose("[TITLE:Save As]", "", 10)
			Sleep(200)

			SendSlow("!fx")
			
			WinWaitClose("[CLASS:DPMDIFrameClass]", "", 10)`
	});
	renameOut = true;
}
