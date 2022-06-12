import {xu} from "xu";
import {Program} from "../../Program.js";

export class hiJaakExpress extends Program
{
	website  = "https://archive.org/details/hijaak-express";
	loc      = "win2k";
	bin      = "c:\\Program Files\\IMSI\\HiJaak Express\\bin\\hjcvt32.exe";
	args     = r => [r.inFile()];
	qemuData = ({
		script : `
			Func MainWindowOrFailure()
				WindowFailure("HiJaak Convert", "Error", 2, "{ESCAPE}")
				return WinActive("HiJaak Convert", "Save as")
			EndFunc
			$mainWindow = CallUntil("MainWindowOrFailure", ${xu.SECOND*10})
			
			Send("c:\\out\\out.bmp{ENTER}")
			WinWaitClose($mainWindow, "", 10)
			
			KillAll("loco.exe")
			KillAll("Hijaak.exe")
			KillAll("hjcvt32.exe")

			Send("{ESCAPE}")
			Send("{ESCAPE}")
			Send("{ESCAPE}")
			Send("{ESCAPE}")
			Send("{ESCAPE}")`
	});
	renameOut = true;
	chain     = "convert";
}
