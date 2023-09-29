import {xu} from "xu";
import {Program} from "../../Program.js";

export class adobeIllustrator extends Program
{
	website  = "https://winworldpc.com/product/adobe-illustrator/80";
	loc      = "winxp";
	bin      = "c:\\Program Files\\Adobe\\Illustrator 8.0\\Illustrator.exe";
	args     = r => [r.inFile()];
	osData   = ({
		script : `
		$mainWindow = WindowRequire("Adobe Illustrator", "", 5)

		Func PreOpenWindows()
			WindowFailure("Adobe Illustrator", "Can't open the illustration", -1, "{ENTER}")
			WindowFailure("DXF Conversion Data", "not a supported element", -1, "{ENTER}")
		EndFunc
		CallUntil("PreOpenWindows", ${xu.SECOND*4})

		WaitForControl($mainWindow, "", "[CLASS:MDIClass]", ${xu.SECOND*7})

		; Vector Save As (exporting as PNG/BMP doesn't seem to work, probably because I didn't install the correct plugins)
		SendSlow("!fa")
		$saveWindow = WindowRequire("Save This Document As:", "", 5)
		Send("c:\\out{ENTER}out{TAB}{DOWN}{END}{ENTER}{ENTER}")
		WinWaitClose($saveWindow, "", 5)
		$epsFormatWindow = WindowRequire("EPS Format", "", 5)
		Send("+{TAB}+{TAB}+{TAB}+{TAB}+{TAB}{UP}{UP}{TAB}{TAB}{TAB}{TAB}{TAB}{ENTER}")
		WinWaitClose($epsFormatWindow, "", 10)

		Sleep(2000)

		Send("^q")
		WinWaitClose($mainWindow, "", 5)`
	});
	renameOut = true;
	chain     = "dexvert[asFormat:image/eps]";
}
