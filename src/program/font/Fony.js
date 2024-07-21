import {xu} from "xu";
import {Program} from "../../Program.js";

export class Fony extends Program
{
	website  = "http://hukka.ncn.fi/?fony";
	loc      = "win2k";
	bin      = "Fony.exe";
	args     = r => [r.inFile()];
	osData   = ({
		quoteArgs : true,
		script : `
			Func MainWindowOrFailure()
				WindowFailure("Error Loading Font", "", -1, "{ESCAPE}")
				return WinActive("Fony", "")
			EndFunc
			$mainWindow = CallUntil("MainWindowOrFailure", ${xu.SECOND*15})
			If Not $mainWindow Then
				$mainWindow = WinExists("Fony", "")
				If Not $mainWindow Then
					Exit 0
				Else
					MouseClick("left", 103, 145)
				EndIf
			EndIf

			SendSlow("!f")
			SendSlow("e{DOWN}{ENTER}")

			$exportWindow = WindowRequire("BDF Export", "", 10)
			Send("{ENTER}")

			$saveAsWindow = WindowRequire("Save As", "", 10)
			Send("c:\\out\\out.bdf{ENTER}")
			WinWaitClose($saveAsWindow, "", 10)

			WaitForStableFileSize("c:\\out\\out.bdf", ${xu.SECOND*3}, ${xu.SECOND*15})
			WinWaitActive($mainWindow, "", 10)
			SendSlow("!fx")`
	});
	renameOut = true;
	chain = "dexvert[asFormat:font/bdf]";
}
