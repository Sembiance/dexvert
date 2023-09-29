import {Program} from "../../Program.js";

export class clipbrdWin2k extends Program
{
	website  = "https://microsoft.com";
	unsafe   = true;
	loc      = "win2k";
	bin      = "c:\\WINNT\\system32\\clipbrd.exe";
	args     = r => [r.inFile()];
	osData   = ({
		script : `
			#include <ScreenCapture.au3>

			$mainWindowVisible = WinWaitActive("ClipBook Viewer", "", 5)
			If $mainWindowVisible Not = 0 Then
				; wait for the clear clipboard warning to appear so we can get rid of it
				$clearVisible = WinWaitActive("Clear Clipboard", "", 15)
				If $clearVisible Not = 0 Then
					ControlClick("Clear Clipboard", "", "[CLASS:Button; TEXT:&No]")
				EndIf

				; switch to the actual clip we opened
				Sleep(500)
				SendSlow("!w1")
				Sleep(2000)

				; open mspaint, paste it and save it as a png
				SaveClipboardWithMSPaint("WINNT", "c:\\out\\out.png")

				Sleep(500)
				SendSlow("!fx")

				WinWaitClose("ClipBook Viewer", "", 5)
			EndIf`});
	renameOut = true;
	chain     = "dexvert[asFormat:image/bmp] -> autoCropImage";
}
