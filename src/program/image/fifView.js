import {xu} from "xu";
import {Program} from "../../Program.js";

export class fifView extends Program
{
	website  = "http://cd.textfiles.com/wthreepack/wthreepack-1/COMPRESS/FIFDEMO.ZIP";
	unsafe   = true;
	loc      = "winxp";
	bin      = "c:\\dexvert\\FIFView\\FIFView.exe";
	args     = r => [r.inFile()];
	osData   = ({
		dontMaximize : true,
		script       : `
		#include <ScreenCapture.au3>

		Local $hasError=0;
		Func ErrorWindows()
			$hasError = WindowDismiss("Error", "", "{ESCAPE}") = 0 ? $hasError : 1
		EndFunc
		CallUntil("ErrorWindows", ${xu.SECOND*3})
		If $hasError Not = 0 Then
			Exit 0
		EndIf

		WindowRequire("[TITLE:Fractal Viewer Helper App; CLASS:DECO_NT_Class]", "", 3)

		_ScreenCapture_CaptureWnd("c:\\out\\out.bmp", WinGetHandle("[TITLE:Fractal Viewer Helper App; CLASS:DECO_NT_Class]"), 4, 42, 644, 441, False);

		Sleep(500)
		SendSlow("!fx")

		WinWaitClose("[TITLE:Fractal Viewer Helper App; CLASS:DECO_NT_Class]", "", 10)`
	});
	renameOut = true;
	chain     = "dexvert[asFormat:image/bmp] -> autoCropImage";
}
