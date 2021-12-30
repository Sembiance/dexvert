import {Program} from "../../Program.js";

export class UniExtract extends Program
{
	website = "https://www.legroom.net/software/uniextract";
	flags   = {
		type : `Which type of extraction to choose. Examples: "i3comp extraction" or "STIX extraction"`
	};
	loc      = "win2k";
	bin      = "c:\\dexvert\\uniextract161\\UniExtract.exe";
	args     = r => [r.inFile()];
	qemuData = r => ({
		script : `
			Local $mainWindow = WinWaitActive("Universal Extractor", "", 10)

			ControlSetText("Universal Extractor", "", "[CLASS:Edit; INSTANCE:2]", "c:\\out\\")
			Sleep(200)

			ControlClick("Universal Extractor", "", "[CLASS:Button; TEXT:&OK]")

			WinWaitClose($mainWindow, "", 10)

			Local $decisionWindow = WinWaitActive("Universal Extractor", "", 5)
			If $decisionWindow Then
				${r.flags.type ? `ControlClick("Universal Extractor", "", "[CLASS:Button; TEXT:${r.flags.type}]")` : ""}
				ControlClick("Universal Extractor", "", "[CLASS:Button; TEXT:&OK]")
			EndIf

			Local $hasError = WinWaitActive("Universal Extractor", "could not be extracted", 5)
			If $hasError Then
				ControlClick("Universal Extractor", "", "[CLASS:Button; TEXT:&Cancel]")
			EndIf

			WinWaitClose("Universal Extractor", "", 10)

			ProcessWaitClose("UniExtract.exe", 5)
			ProcessClose("Expander.exe")`
	});
	renameOut = false;
}
