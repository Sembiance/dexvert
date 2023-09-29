import {xu} from "xu";
import {Program} from "../../Program.js";

export class frameMaker extends Program
{
	website  = "https://winworldpc.com/product/framemaker/50";
	unsafe   = true;
	loc      = "win2k";
	bin      = "c:\\MAKER5\\FRAME.EXE";
	args     = r => [r.inFile()];
	osData   = ({
		script : `
			$mainWindow = WindowRequire("FrameMaker", "", 5)
			Func PreOpenWindows()
				WindowDismiss("FrameMaker", "will be converted to the current release", "{ENTER}")
				WindowDismiss("FrameMaker", "unavailable font", "{ENTER}")
				WindowDismiss("FrameMaker", "unavailable language", "{ENTER}")
				WindowDismiss("Missing File", "", "{TAB}{TAB}{TAB}{TAB}{TAB}{DOWN}{DOWN}{ENTER}")
				WindowDismiss("FrameMaker", "Cannot display", "{ENTER}")
				WindowDismiss("FrameMaker", "does not exist", "{ENTER}")
			EndFunc
			CallUntil("PreOpenWindows", ${xu.SECOND*4})

			SendSlow("!fa", 250)

			$saveAsWindow = WindowRequire("Save Document", "", 5)
			Send("c:\\out\\out.rtf{TAB}{TAB}{TAB}{TAB}{TAB}r{ENTER}")
			WinWaitClose($saveAsWindow, "", 5)

			SendSlow("!fx", 250)

			Func PostExitWindows()
				WindowDismiss("FrameMaker", "Unsaved", "n")
			EndFunc
			CallUntil("PostExitWindows", ${xu.SECOND*3})`
	});
	chain     = "dexvert[asFormat:document/rtf]";
	renameOut = true;
}
