import {xu} from "xu";
import {Program} from "../../Program.js";

export class pageMaker7 extends Program
{
	website  = "https://archive.org/details/adobe-page-maker-7.0-with-serial-key-pwd-12345_20221219";
	loc      = "win7";
	bin      = "c:\\Program Files\\Adobe\\PageMaker 7.0\\Pm70.exe";
	args     = r => [r.inFile()];
	osData   = ({
		script : `
			$mainWindow = WindowRequire("Adobe PageMaker 7.0", "", 20)
			Func PreOpenWindows()
				WindowFailure("Adobe PageMaker", "Cannot open file", -1, "{ENTER}")
				WindowDismiss("[TITLE:Adobe PageMaker]", "Cannot load your target printer", "{ENTER}")
				WindowDismiss("[TITLE:PANOSE Font Matching Results]", "", "{ENTER}")
				WindowDismiss("Lost Link", "", "!a")
				WindowDismiss("[TITLE:Adobe PageMaker]", "HyperContent Manager error", "{ENTER}")
			EndFunc
			CallUntil("PreOpenWindows", ${xu.SECOND*7})

			SendSlow("!fp")

			$printWindow = WindowRequire("Print Document", "", 5)
			Send("{ENTER}")
			WinWaitClose($printWindow, "", 10)

			HandleCutePDFPrint()

			WinWaitActive($mainWindow, "", 5)

			Send("^q")`
	});
	renameOut = true;
}
