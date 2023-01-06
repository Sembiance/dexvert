import {xu} from "xu";
import {Program} from "../../Program.js";

export class pageMaker5 extends Program
{
	website  = "https://winworldpc.com/product/aldus-pagemaker/50";
	loc      = "win2k";
	bin      = "c:\\dexvert\\PM5\\PM5.exe";
	args     = r => [r.inFile()];
	qemuData = ({
		alsoKill  : ["ntvdm.exe"],
		scriptPre : `
			;DirRemove("c:\\dexvert\\ALDUS", 1)
			DirCopy("c:\\dexvert\\ALDUS5", "c:\\dexvert\\ALDUS", 1)`,
		script : `
			$mainWindow = WindowRequire("Aldus PageMaker 5.0", "", 5)
			Func PreOpenWindows()
				WindowFailure("PageMaker", "Cannot open file", -1, "{ENTER}")
				WindowDismiss("PageMaker", "Inconsistencies in your pub", "{ENTER}")
				WindowDismiss("PageMaker 5.0", "Deleted text remains", "n")
				WindowDismiss("PageMaker", "Cannot load driver", "{ENTER}")
				WindowDismiss("", "PANOSE font matching results", "{ENTER}")
				WindowDismiss("", "Translation options for", "{ENTER}")
			EndFunc
			CallUntil("PreOpenWindows", ${xu.SECOND*3})

			Send("^p")

			$printWindow = WindowRequire("Print", "", 5)
			Send("{ENTER}")

			$printAsWindow = WindowRequire("Save PDF File As", "", 5)
			Send("c:\\out\\out.pdf{ENTER}")
			WinWaitClose($printAsWindow, "", 3)

			Func PostPrintWindows()
				WindowDismiss("[TITLE:Printers Folder]", "There was an error", "{TAB}{SPACE}")
			EndFunc
			CallUntil("PostPrintWindows", ${xu.SECOND*3})

			Send("^q")

			Func PostQuitWindows()
				WindowDismiss("[TITLE:Aldus PageMaker 5.0]", "before closing?", "n")
			EndFunc
			CallUntil("PostQuitWindows", ${xu.SECOND*3})
			WinWaitClose($mainWindow, "", 3)`
	});
	renameOut = true;
}
// Pptd40nt.exe