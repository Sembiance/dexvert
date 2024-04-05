import {xu} from "xu";
import {Program} from "../../Program.js";

export class canvas5 extends Program
{
	website  = "https://winworldpc.com/product/deneba-canvas/5x";
	loc      = "win2k";
	bin      = "c:\\Canvas5\\Canvas5.exe";
	flags   = {
		vector : "Set this to true and it will be converted as a vector image."
	};
	args     = r => [r.inFile()];
	osData   = r => ({
		script   : `
			AutoItSetOption("SendKeyDelay", 40)

			Func PreOpenWindows()
				WindowFailure("Canvas Alert", "Error loading document", -1, "{ENTER}")
				WindowFailure("Canvas Alert", "Out of memory", -1, "{ENTER}")
				WindowDismiss("Choose Resolution", "", "{ENTER}")
				WindowDismiss("Font Matching", "", "{ENTER}")
				WindowDismiss("Select Layout", "", "{ENTER}")
				WindowDismiss("Acquire Page", "", "{ENTER}")
				If WinActive("CGM Import Options") Then
					ControlClick("CGM Import Options", "", "[CLASS:CVButtonClass; TEXT:OK]")
				EndIf
				If WinActive("Canvas 5 - [") Then
					return ControlGetHandle("Canvas 5 - [", "", "[CLASS:ViewClass]")
				EndIf
			EndFunc

			$mainWindow = CallUntil("PreOpenWindows", ${xu.MINUTE})

			Sleep(500)
			SendSlow("^+s")

			$saveWindow = WindowRequire("Save", "", 10)
			Send("c:\\out\\out.${r.flags.vector ? "eps" : "TIFF"}{TAB}{DOWN}${r.flags.vector ? "ee{ENTER}" : "{END}{UP}{ENTER}"}")
			WindowDismissWait("Warning!", "", 3, "y")
			Send("{ENTER}")
			WinWaitClose($saveWindow, "", 5)
			
			Func PostExportWindows()
				WindowDismiss("Export TIFF", "", "{ENTER}")
				WindowDismiss("Render", "", "{ENTER}")
				WindowDismiss("EPSF Export Options", "", "{ENTER}")
				WindowDismiss("Indexed Color", "", "{ENTER}")
				return WinActive($mainWindow, "")
			EndFunc
			CallUntil("PostExportWindows", ${xu.SECOND*7})
			WaitForStableFileSize("c:\\out\\out.TIF", ${xu.SECOND*2}, ${xu.MINUTE})

			; do not be tempted to just exit, canvas 5 is sensitive to being killed and it can mess up the entire install
			Send("!x")
			WinWaitClose($mainWindow, "", 5)
			WaitForPID("Canvas5.exe", ${xu.SECOND*10})`
	});
	renameOut = true;
	chain     = r => `dexvert[asFormat:${r.flags.vector ? "image/eps" : "image/tiff"}]`;
}
