import {xu} from "xu";
import {Program} from "../../Program.js";

export class qtPicViewer extends Program
{
	website  = "https://github.com/Sembiance/dexvert/tree/master/os/aux/winxp/app/qtw2";
	unsafe   = true;
	loc      = "winxp";
	bin      = "C:\\WINDOWS\\VIEWER.EXE";
	args     = r => [r.inFile()];
	osData   = ({
		alsoKill : ["qtnotify.exe", "ntvdm.exe"],
		script   : `
			Func ErrorWindows()
				WindowFailure("", "Could not open file", -1, "{ESCAPE}")
				WindowFailure("", "Could not get picture", -1, "{ESCAPE}")
				WindowFailure("[CLASS:#32770]", "", -1, "{ESCAPE}")
			EndFunc

			;Wait for the picture sub window/control to appear
			$mainWinActive = WinWaitActive("[TITLE:Picture Viewer]", "", 10)
			If $mainWinActive Not = 0 Then
				CallUntil("ErrorWindows", ${xu.SECOND*3})
				
				WaitForControl("[TITLE:Picture Viewer]", "", "[CLASS:ViewerPictureClass]", ${xu.SECOND*10})
			
				Sleep(500)

				SendSlow("!ec")

				Sleep(250)

				SendSlow("!fx")

				WinWaitClose("[TITLE:Picture Viewer]", "", 10)

				SaveClipboardWithMSPaint("WINDOWS", "c:\\out\\out.png")
			EndIf`});
	renameOut = true;
}
