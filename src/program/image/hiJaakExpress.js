import {Program} from "../../Program.js";

export class hiJaakExpress extends Program
{
	website  = "https://archive.org/details/hijaak-express";
	loc      = "win2k";
	bin      = "c:\\Program Files\\IMSI\\HiJaak Express\\bin\\hjcvt32.exe";
	args     = r => [r.inFile()];
	qemuData = ({
		script : `
			$convertWindow = WinWaitActive("HiJaak Convert", "", 5)
			If $convertWindow Not = 0 Then
				Send("c:\\out\\out.bmp{ENTER}")
				WinWaitClose("HiJaak Convert", "", 20)
			EndIf
			
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
