import {Program} from "../../Program.js";
import {runUtil} from "xutil";

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
	post = async r => await runUtil.run("convert", [r.f.new.absolute, "-bordercolor", "#FFFFFF", "-border", "1x1", "-fuzz", "20%", "-trim", "+repage", r.f.new.absolute]);
	chain = "dexvert[asFormat:image/bmp]"
}
