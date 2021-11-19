import {Program} from "../../Program.js";

export class fifView extends Program
{
	website  = "http://cd.textfiles.com/wthreepack/wthreepack-1/COMPRESS/FIFDEMO.ZIP";
	unsafe   = true;
	loc      = "winxp";
	bin      = "c:\\dexvert\\FIFView\\FIFView.exe"
	args     = r => [r.inFile()]
	qemuData = () => ({
		dontMaximize : true,
		script : `
		#include <ScreenCapture.au3>

		WinWaitActive("[TITLE:Fractal Viewer Helper App; CLASS:DECO_NT_Class]", "", 10)
		Sleep(1000)

		_ScreenCapture_CaptureWnd("c:\\out\\out.bmp", WinGetHandle("[TITLE:Fractal Viewer Helper App; CLASS:DECO_NT_Class]"), 4, 42, 644, 441, False);

		Sleep(500)
		Send("!f")
		Sleep(100)
		Send("x")

		WinWaitClose("[TITLE:Fractal Viewer Helper App; CLASS:DECO_NT_Class]", "", 10)`
	});
	chain = "dexvert[asFormat:image/bmp] -> autoCropImage"
}
