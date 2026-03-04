import {xu} from "xu";
import {Program} from "../../Program.js";

export class totalCommander extends Program
{
	website = "https://totalcmd.net/plugring/totalcmd.html";
	loc     = "win7";
	bin     = "c:\\Program Files\\totalcmd\\TOTALCMD.EXE";
	args    = r => [r.inFile(), "c:\\out", "/A"];
	notes   = "Has the plugin: https://totalcmd.net/plugring/resextract.html";
	osData  = ({
		script : `
			$mainWindow = WindowRequire("Total Commander 11.02 - ", "", 10)
			Sleep(500)
			Send("!{F9}")
			$unpackWindow = WindowRequire("Unpack files", "", 10)
			Send("{ENTER}")
			WinWaitClose($unpackWindow, "", 15)

			Sleep(2000)

			Func WaitForUnpackComplete()
				If WinActive("[CLASS:TOverWriteForm]", "") Then
					SendSlow(">{DOWN}{DOWN}{ENTER}")
				EndIf
				return Not WinExists("[CLASS:TDLG2FILEACTIONMIN]", "") And WinActive($mainWindow, "")
			EndFunc
			CallUntil("WaitForUnpackComplete", ${xu.SECOND*20})
			Send("!f")
			Sleep(250)
			Send("q")`
	});
	renameOut = false;
}
