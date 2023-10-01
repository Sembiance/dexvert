import {xu} from "xu";
import {path} from "std";
import {Program} from "../../Program.js";

export class imjview extends Program
{
	website  = "https://github.com/Sembiance/dexvert/blob/master/os/aux/winxp/app/IMPACJ11.ZIP";
	unsafe   = true;
	loc      = "winxp";
	bin      = "c:\\dexvert\\IMPACJ11\\IMJVIEW.EXE";
	args     = () => [];
	osData   = r => ({
		alsoKill : ["ntvdm.exe"],
		script   : `
			#include <ScreenCapture.au3>

			; extension must be .imj
			FileMove("c:\\in\\${path.basename(r.inFile())}", "c:\\in\\in.imj")

			$mainWindow = WindowRequire("Pegasus IMPACJ Demonstration Product", "", 7)
			Send("{ENTER}");
			WinWaitClose($mainWindow, "", 5)
			SendSlow("!io", 250);
			Sleep(500);

			$openWindow = WindowRequire("Open", "", 5)
			Send("c:\\in\\in.imj{ENTER}")
			WinWaitClose($openWindow, "", 5)

			WindowFailure("Error", "Unable to display", 3, "{ENTER}")

			$viewWindowControl = WaitForControl("[CLASS:imjview frame]", "", "[CLASS:imjview child]", ${xu.SECOND*5})
			If $viewWindowControl Not = 0 Then
				$viewDim = WinGetClientSize($viewWindowControl)
				_ScreenCapture_CaptureWnd("c:\\out\\out.bmp", $viewWindowControl, 4, 23, $viewDim[0]-4, $viewDim[1]-4, False)
			EndIf

			SendSlow("!ix");`});
	renameOut = true;
	chain     = "dexvert[asFormat:image/bmp]";
}
