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
				WindowFailure("[TITLE:Error Loading Font]", "", -1, "{ESCAPE}")
				return WinActive("[CLASS:TFMain]", "")
			EndFunc
			$mainWindow = CallUntil("MainWindowOrFailure", ${xu.SECOND*15})
			If Not $mainWindow Then
				Exit 0
			EndIf

			SendSlow("!fe{DOWN}{ENTER}")

			$exportWindow = WindowRequire("[CLASS:TFBDFExport; TITLE:BDF Export]", "", 10)
			ControlClick($exportWindow, "", "[CLASS:TButton; TEXT:OK]")

			$saveAsWindow = WindowRequire("[TITLE:Save As]", "", 10)
			ControlClick($saveAsWindow, "", "[CLASS:Edit]")
			Send("{HOME}c:\\out\\")
			ControlClick($saveAsWindow, "", "[CLASS:Button; TEXT:&Save]")

			WinWaitActive($mainWindow, "", 10)
			SendSlow("!fx")`
	});
	renameOut = true;
	chain = "dexvert[asFormat:font/bdf]";
}
