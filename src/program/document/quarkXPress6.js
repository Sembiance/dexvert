import {xu} from "xu";
import {Program} from "../../Program.js";


export class quarkXPress6 extends Program
{
	website  = "https://archive.org/details/quarkxpress6.1version6.1r02004";
	loc      = "win7";
	bin      = "c:\\Program Files\\Quark\\QuarkXPress 6.1\\QuarkXPress Passport.exe";
	args     = r => [r.inFile()];
	osData   = ({
		script : `
			Func ProjectIsOpen()
				$control = ControlGetHandle("", "", "[CLASS:XPressMDIProject]")
				If Not $control Then
					return 0
				EndIf

				$text = ControlGetText("", "", $control)
				If StringInStr($text, "in : in") Then
					return 1
				EndIf

				return 0
			EndFunc

			Func PreOpenWindows()
				WindowDismiss("Activate QuarkXPress 6.1", "", "{TAB}{ENTER}")
				WindowDismiss("[TITLE:QuarkXPress (tm)]", "Some settings saved with this project are different", "{ENTER}")
				WindowDismiss("[TITLE:QuarkXPress (tm)]", "uses fonts not installed", "{TAB}{ENTER}")
				WindowFailure("[TITLE:QuarkXPress (tm)]", "This file is not a valid Quark", -1, "{ESCAPE}")
				return ProjectIsOpen()
			EndFunc
			$projectOpenAndReady = CallUntil("PreOpenWindows", ${xu.SECOND*30})
			If Not $projectOpenAndReady Then
				Exit 0
			EndIf

			Send("^p")

			Func PrePrintWindows()
				WindowDismiss("[TITLE:QuarkXPress (tm)]", "This document was built with other", "{ENTER}")
				return WinActive("Print in", "")
			EndFunc
			$printWindow = CallUntil("PrePrintWindows", ${xu.SECOND*7})

			Send("{ENTER}")

			HandleCutePDFPrint()`
	});
	renameOut = true;
}
