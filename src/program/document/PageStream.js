import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class PageStream extends Program
{
	website   = "https://pagestream.org/";
	loc       = "wine";
	bin       = "c:\\dexvert\\PageStream\\PageStream5.exe";
	exclusive = "wine";
	notes     = "This program is very finicky and fragile and slow. Often the PDF generation doesn't work and Print to PDF doesn't work either. Installed is version 5. I tried updated to 5.1.2 and it was WORSE. Bleh.";
	wineData  = r => ({
		cwd    : "wine://dexvert/PageStream",
		script : `
			$mainWindow = WindowRequire("PageStream5", "", 5)
			Sleep(1000)
			MouseClick("left", 100, 100)
			Sleep(250)
			Send("^o")

			$openWindow = WindowRequire("Open Document", "", 5)
			SendSlow("c:\\in${r.wineCounter}\\${path.basename(r.inFile())}{ENTER}")
			WinWaitClose($openWindow, "", 5)

			Sleep(500)
			Send("{ENTER}")

			$fontSubstitutionWindow = WinWait("Font Substitution", "", 10)
			ControlClick($fontSubstitutionWindow, "", "[CLASS:Button; TEXT:OK]")

			$mainWindow = WindowRequire("PageStream5", "", 5)
			Sleep(1000)

			SendSlow("!fD")

			$saveAsPDFWindow = WindowRequire("Save As PDF", "", 10)
			ControlClick($saveAsPDFWindow, "", "[CLASS:Button; TEXT:Save]")
			
			$saveAsPDFWindow = WindowRequire("Save as PDF", "", 10)	; note the slightly different spelling, rofl, what a train wreck
			SendSlow("c:\\out${r.wineCounter}\\out.pdf{ENTER}")
			WinWaitClose($saveAsPDFWindow, "", 10)

			WaitForStableFileSize("c:\\out${r.wineCounter}\\out.pdf", ${xu.SECOND*5}, ${xu.SECOND*30})

			WinWaitActive($mainWindow, "", 2)
			
			Send("^q")`
	});
	renameOut = true;
}
