import {xu} from "xu";
import {Program} from "../../Program.js";

export class qtPicViewer extends Program
{
	website  = "https://github.com/Sembiance/dexvert/tree/master/qemu/winxp/data/app/qtw2";
	unsafe   = true;
	loc      = "winxp";
	bin      = "C:\\WINDOWS\\VIEWER.EXE";
	args     = r => [r.inFile()];
	qemuData = ({
		script : `
			;Wait for the picture sub window/control to appear
			$mainWinActive = WinWaitActive("[TITLE:Picture Viewer]", "", 10)
			If $mainWinActive Not = 0 Then
				$errorVisible = WinWaitActive("[CLASS:#32770]", "", 1)
				If $errorVisible Not = 0 Then
					Send("{ESCAPE}")
					Sleep(100)
					Send("!f")
					Sleep(200)
					Send("x")
				Else
					WaitForControl("[TITLE:Picture Viewer]", "", "[CLASS:ViewerPictureClass]", ${xu.SECOND*10})
				
					Sleep(500)

					Send("!e")
					Sleep(200)
					Send("c")

					Sleep(250)

					Send("!f")
					Sleep(200)
					Send("x")

					WinWaitClose("[TITLE:Picture Viewer]", "", 10)

					SaveClipboardWithMSPaint("WINDOWS", "c:\\out\\out.png")
				EndIf
			EndIf
			
			KillAll("viewer.exe")`});
	renameOut = true;
}
