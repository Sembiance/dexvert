import {Program} from "../../Program.js";

export class PageStream extends Program
{
	website  = "https://pagestream.org/";
	loc      = "win2k";
	bin      = "c:\\PageStream\\PageStream5.exe";
	notes    = "This program is very finicky and fragile and slow. Often the PDF generation doesn't work and Print to PDF doesn't work either. Installed is version 5. I tried updated to 5.1.2 and it was WORSE. Bleh.";
	args     = r => [r.inFile()];
	osData   = ({
		script : `
			; NOTE! We can't use WindowsRequire and WinWaitActive because PageStream5 has a stupid 'Tooltip' window that is actually active that you can't get rid of
			$selectModuleWindow = WinWait("Select Module...", "", 10)
			ControlClick($selectModuleWindow, "", "[CLASS:Button; TEXT:OK]")
			WinWaitClose($selectModuleWindow, "", 5)

			$fontSubstitutionWindow = WinWait("Font Substitution", "", 10)
			ControlClick($fontSubstitutionWindow, "", "[CLASS:Button; TEXT:OK]")

			$mainWindow = WindowRequire("PageStream5", "", 5)
			Sleep(1000)

			SendSlow("!fD")

			$saveAsPDFWindow = WindowRequire("Save As PDF", "", 10)
			ControlClick($saveAsPDFWindow, "", "[CLASS:Button; TEXT:Save]")
			
			$saveAsPDFWindow = WindowRequire("Save as PDF", "", 10)	; note the slightly different spelling
			Send("c:\\out\\out.pdf{ENTER}")
			WinWaitClose($saveAsPDFWindow, "", 10)

			$pleaseWaitWindow = WinWait("Please Wait", "", 10)
			WinWaitClose($pleaseWaitWindow, "", 10)

			WinWaitActive($mainWindow, "", 10)
			
			Send("^q")`
	});
	renameOut = true;
}
