import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class pageMaker4 extends Program
{
	website  = "https://winworldpc.com/product/aldus-pagemaker/40";
	loc      = "win7";
	bin      = "c:\\PM4\\PM4.exe";
	args     = r => [r.inFile()];
	osData   = r => ({
		scriptPre : `
			DirRemove("c:\\ALDUS", 1)
			DirCopy("c:\\dexvert\\ALDUS4", "c:\\ALDUS", 1)`,
		script : `
			$mainWindow = WindowRequire("PageMaker 4.0", "", 5)
			Func PreOpenWindows()
				WindowFailure("PageMaker", "Cannot open file", -1, "{ENTER}")
				WindowDismiss("PageMaker", "Inconsistencies in your pub", "{ENTER}")
				WindowDismiss("PageMaker 4.0", "Deleted text remains", "n")
				WindowDismiss("PageMaker", "Cannot load driver", "{ENTER}")
				If ControlGetHandle("", "", "[CLASS:Button; TEXT:Ignore &all]") Then
					Send("!a")
				EndIf
			EndFunc
			CallUntil("PreOpenWindows", ${xu.SECOND*4})

			$docWindow = WindowRequire("", "C:\\IN\\${path.basename(r.inFile()).toUpperCase()}", 25)

			Send("^p")

			Sleep(2000)
			Send("{ENTER}")

			If WindowDismissWait("PageMaker 4.0", "Page and paper orientation", 5, "{TAB}{SPACE}") Not = 0 Then
				Sleep(1000)
				SendSlow("!s{TAB}{TAB}{TAB}{TAB}{TAB}{TAB}{DOWN}{ENTER}^p")
				Sleep(2000)
				Send("{ENTER}")
			EndIf

			Func PostPrintWindows()
				WindowDismiss("[TITLE:PageMaker 4.0]", "Publication was not composed", "{ENTER}")
				If ControlGetHandle("", "", "[CLASS:Button; TEXT:&Print pub]") Then
					Send("!p")
				EndIf
			EndFunc
			CallUntil("PostPrintWindows", ${xu.SECOND*3})

			HandleCutePDFPrint()

			Func PostPrintAsWindows()
				WindowDismiss("[TITLE:Printers Folder]", "There was an error", "{TAB}{SPACE}")
			EndFunc
			CallUntil("PostPrintAsWindows", ${xu.SECOND*3})
			
			Send("^q")`
	});
	renameOut = true;
}
