import {xu} from "xu";
import {Program} from "../../Program.js";

export class pageMaker7 extends Program
{
	website  = "https://archive.org/details/adobe-page-maker-7.0-with-serial-key-pwd-12345_20221219";
	loc      = "winxp";
	bin      = "c:\\Program Files\\Adobe\\PageMaker 7.0\\Pm70.exe";
	args     = r => [r.inFile()];
	osData   = ({
		script : `
			$mainWindow = WindowRequire("Adobe PageMaker 7.0", "", 10)
			Func PreOpenWindows()
				WindowFailure("Adobe PageMaker", "Cannot open file", -1, "{ENTER}")
				WindowDismiss("[TITLE:Adobe PageMaker]", "Cannot load your target printer", "{ENTER}")
				WindowDismiss("[TITLE:PANOSE Font Matching Results]", "", "{ENTER}")
				WindowDismiss("Lost Link", "", "!a")
				WindowDismiss("[TITLE:Adobe PageMaker]", "HyperContent Manager error", "{ENTER}")
			EndFunc
			CallUntil("PreOpenWindows", ${xu.SECOND*4})

			Send("^S")

			$saveAsWindow = WindowRequire("Save Publication", "", 5)
			Send("c:\\TEMP\\document.pmd{ENTER}")

			Func PostSaveAsWindows()
				WindowDismiss("[TITLE:Adobe PageMaker]", "Cannot save as", "{ENTER}")
				WindowDismiss("Save Publication", "Do you want to replace", "y")
			EndFunc
			CallUntil("PostSaveAsWindows", ${xu.SECOND*2})

			WinWaitClose($saveAsWindow, "", 5)

			SendSlow("!fep")

			Func PreExportWindows()
				WindowDismiss("[TITLE:Adobe PageMaker]", "This publication is not currently in a saved state", "y")
			EndFunc
			CallUntil("PreExportWindows", ${xu.SECOND*2})

			$pdfOptionsWindow = WindowRequire("PDF Options", "", 5)
			Send("e")
			
			Func PostPDFOptionsWindows()
				WindowDismiss("[TITLE:Printer Style Warnings]", "", "{ENTER}")
			EndFunc
			CallUntil("PostPDFOptionsWindows", ${xu.SECOND*2})

			$exportAsWindow = WindowRequire("Export PDF As", "", 5)
			Send("c:\\out\\out.pdf{TAB}{TAB}{TAB}{TAB}{SPACE}s")
			WinWaitClose($exportAsWindow, "", 3)

			Func PostExportWindows()
				WindowDismiss("[TITLE:Adobe PageMaker]", "One or more of the linked", "p")
				WindowDismiss("[TITLE:Adobe PageMaker]", "Unable to open the publication", "{ENTER}")
			EndFunc
			CallUntil("PostExportWindows", ${xu.SECOND*3})
			WinWaitClose($pdfOptionsWindow, "", 3)

			WinWaitActive($mainWindow, "", 3)

			Send("^q")`
	});
	renameOut = true;
}
