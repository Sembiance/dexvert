import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class smartDraw6 extends Program
{
	website  = "https://archive.org/details/twilight-dvd069";
	unsafe   = true;
	loc      = "win2k";
	bin      = "c:\\SmartDraw6\\SmartDraw.exe";
	args     = r => [r.inFile()];
	osData   = r => ({
		script : `
			Func MainWindowOrFailure()
				WindowFailure("SmartDraw Professional", "Unable to open file", -1, "{ESCAPE}")
				return WinActive("SmartDraw Professional - [${path.basename(r.inFile())}]", "")
			EndFunc
			$mainWindow = CallUntil("MainWindowOrFailure", ${xu.SECOND*10})
			If Not $mainWindow Then
				Exit 0
			EndIf

			Send("!f")
			Send("e")

			$exportWindow = WindowRequire("Export", "", 10)
			Send("c:\\out\\out.wmf{ENTER}")
			WinWaitClose("Export", "", 10)
			WaitForStableFileSize("c:\\out\\out.wmf", ${xu.SECOND*3}, ${xu.SECOND*15})

			Send("!f")
			Send("x")`});
	renameOut = true;
	chain     = "dexvert[asFormat:image/wmf]";
}
