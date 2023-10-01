import {xu} from "xu";
import {Program} from "../../Program.js";

export class picturePublisher extends Program
{
	website  = "https://winworldpc.com/product/micrografx-graphics-suite/2";
	loc      = "winxp";
	bin      = "c:\\Program Files\\Micrografx\\Picture Publisher\\Pp70.exe";
	args     = r => [r.inFile()];
	osData   = r => ({
		timeout : xu.MINUTE*2,
		script  : `
		$mainWindow = WindowRequire("Micrografx Picture Publisher", "", 5)

		Func PhotoCDOpenDismiss()
			Send("{TAB}{TAB}{TAB}{END}")
			MouseClick("left", 411, 260, 2, 0)
			Send("{ENTER}")
		EndFunc

		Func PreOpenWindows()
			WindowFailure("Micrografx Picture Publisher", "This file type is not supported", -1, "{ESCAPE}")
			WindowFailure("Micrografx Picture Publisher", "Translation failed", -1, "{ESCAPE}")
			WindowFailure("Micrografx Picture Publisher", "Error - File signature mismatch.", -1, "{ESCAPE}")
			WindowDismiss("${r.f.input.base}", "Image Type", "{ENTER}")
			WindowDismiss("Photo CD Open", "", 0, "PhotoCDOpenDismiss")
		EndFunc
		CallUntil("PreOpenWindows", ${xu.SECOND*4})	; some file types like cdr take a while to render

		Send("^!a")

		$saveAsWindow = WindowRequire("Save As", "", 5)
		Send("c:\\out\\out{TAB}w{ENTER}")
		WinWaitClose($saveAsWindow, "", 5)

		WinWaitActive($mainWindow, "", 3)
		SendSlow("!fx")`
	});
	renameOut = true;
	chain     = "dexvert[asFormat:image/bmp]";
}
