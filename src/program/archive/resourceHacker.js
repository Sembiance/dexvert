import {xu} from "xu";
import {Program} from "../../Program.js";

export class resourceHacker extends Program
{
	website  = "http://www.angusj.com/resourcehacker/";
	loc      = "winxp";
	bin      = "c:\\dexvert\\resource_hacker\\ResourceHacker.exe";
	args     = r => [r.inFile()];
	osData   = ({
		script : `
			Func PreOpenWindows()
				$controlHandle = ControlGetHandle("Resource Hacker", "", "[CLASS:TButton; INSTANCE:1; TEXT:&OK]")
				If $controlHandle Then
					ControlClick("Resource Hacker", "", $controlHandle)
					Exit 0
				EndIf
			EndFunc
			CallUntil("PreOpenWindows", ${xu.SECOND*2})
			
			$mainWindow = WindowRequire("Resource Hacker", "", 10)

			Send("!a")
			Sleep(250)
			Send("{DOWN}{DOWN}{DOWN}{DOWN}{DOWN}{DOWN}{DOWN}{ENTER}")

			$saveResourceWindow = WindowRequire("Save resources to", "", 10)
			Send("c:\\out\\out.rc{ENTER}")
			WinWaitClose($saveResourceWindow, "", 10)

			Sleep(200)
			
			SendSlow("!fx")`
	});
	renameOut = {
		alwaysRename : true,
		renamer      : [({fn, originalInput}) => (originalInput && fn==="out.rc" ? [originalInput.name, ".rc"] : [fn])]
	};
}
