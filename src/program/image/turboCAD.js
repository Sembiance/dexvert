import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class turboCAD extends Program
{
	website  = "https://archive.org/details/onyxdvd-16";
	unsafe   = true;
	loc      = "winxp";
	bin      = "c:\\Program Files\\IMSI\\TCW90\\Program\\Tcw90.exe";
	args     = r => [r.inFile()];
	osData   = r => ({
		script : `
			Func MainWindowOrFailure()
				WindowDismiss("FindNews", "", "{ENTER}")
				WindowFailure("SWiSH", "This file appears to have been", -1, "{ENTER}")
				return WinActive("TurboCAD v9.0 - [${path.basename(r.inFile())}", "")
			EndFunc
			$mainWindow = CallUntil("MainWindowOrFailure", ${xu.SECOND*40})
			If Not $mainWindow Then
				Exit 0
			EndIf
			Sleep(3000)
			Send("!fa")

			$saveAsWindow = WindowRequire("Save As", "", 15)
			SendSlow("{TAB}dddd+{TAB}")
			Send("c:\\out\\out.dxf{ENTER}")
			WinWaitClose($saveAsWindow, "", 15)
			WaitForStableFileSize("c:\\out\\out.dxf", ${xu.SECOND*2}, ${xu.SECOND*30})
			Send("!fx")
			`});
	renameOut = true;
	chain     = "ezdxf";
}
