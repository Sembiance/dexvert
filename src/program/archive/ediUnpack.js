import {xu} from "xu";
import {Program} from "../../Program.js";

export class ediUnpack extends Program
{
	website  = "https://github.com/Sembiance/dexvert/blob/master/os/aux/win2k/app/UNPACK.EXE";
	loc      = "win2k";
	bin      = "c:\\dexvert\\UNPACK.exe";
	args     = r => [r.inFile()];
	osData   = ({
		// Sadly, the program crashes instantly as soon as I try and use AutoIt window info to find buttons, so we resort to X/Y screen coordinates and cross our fingers
		script : `
			; There is no keyboard control of the menus here, so we have to determine how many folders before in/out and click on the proper pixel
			Local $cDirs = ListCDirs()

			$mainWindow = WindowRequire("EDI Unpack - V2.00", "", 10)
			MouseClick("left", 316, 96, 2, 0)
			MouseClick("left", 316, 70+((_ArraySearch($cDirs, "out")-1)*14), 2, 0)

			Sleep(200)
			MouseClick("left", 25, 156, 1, 0)
			Sleep(200)
			MouseClick("left", 235, 75, 1, 0)
			
			Sleep(200)
			MouseClick("left", 1013, 8, 1, 0)

			Local $errorOKControl = WaitForControl("[TITLE:in$]", "", "[CLASS:Button; TEXT:OK]", ${xu.SECOND*3})
			If $errorOKControl Then
				ControlClick("[TITLE:in$]", "", "[CLASS:Button; TEXT:OK]")
			EndIf

			WinWaitClose($mainWindow, "", 10)`
	});
	renameOut = false;
}
