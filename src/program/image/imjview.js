import {xu} from "xu";
import {path} from "std";
import {Program} from "../../Program.js";

export class imjview extends Program
{
	website  = "https://github.com/Sembiance/dexvert/blob/master/qemu/winxp/data/app/IMPACJ11.ZIP";
	unsafe   = true;
	loc      = "winxp";
	bin      = "c:\\dexvert\\IMPACJ11\\IMJVIEW.EXE";
	args     = () => [];
	qemuData = r => ({
		alsoKill : ["ntvdm.exe"],
		script   : `
			#include <ScreenCapture.au3>

			; extension must be .imj
			FileMove("c:\\in\\${path.basename(r.inFile())}", "c:\\in\\in.imj")

			$mainWindow = WinWaitActive("Pegasus IMPACJ Demonstration Product", "", 5)
			If $mainWindow Not = 0 Then
				Send("{ENTER}");
				WinWaitClose("Pegasus IMPACJ Demonstration Product", "", 5)
				Send("!i");
				Sleep(250);
				Send("o");
				Sleep(500);

				$openWindow = WinWaitActive("Open", "", 5)
				If $openWindow Not = 0 Then
					Send("c:\\in\\in.imj{ENTER}")
				EndIf

				WinWaitClose("Open", "", 5)

				WindowFailure("Error", "Unable to display", 3, "{ENTER}")

				$viewWindowControl = WaitForControl("[CLASS:imjview frame]", "", "[CLASS:imjview child]", ${xu.SECOND*5})
				If $viewWindowControl Not = 0 Then
					$viewDim = WinGetClientSize($viewWindowControl)
					_ScreenCapture_CaptureWnd("c:\\out\\out.bmp", $viewWindowControl, 4, 23, $viewDim[0]-4, $viewDim[1]-4, False)
				EndIf

				Send("!i");
				Sleep(250);
				Send("x");
			EndIf`});
	renameOut = true;
	chain     = "dexvert[asFormat:image/bmp]";
}
