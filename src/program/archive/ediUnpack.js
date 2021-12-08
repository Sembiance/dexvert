import {xu} from "xu";
import {Program} from "../../Program.js";

export class ediUnpack extends Program
{
	website  = "https://github.com/Sembiance/dexvert/blob/master/qemu/win2k/data/app/UNPACK.EXE";
	loc      = "win2k";
	bin      = "c:\\dexvert\\UNPACK.exe";
	args     = r => [r.inFile()];
	qemuData = ({
		// Sadly, the program crashes instantly as soon as I try and use AutoIt window info to find buttons, so we resort to X/Y screen coordinates and cross our fingers
		script : `
			Sleep(2000)
			MouseClick("left", 316, 86, 2, 0)
			Sleep(1000)
			MouseClick("left", 316, 125, 2, 0)
			Sleep(1000)
			MouseClick("left", 25, 156, 1, 0)
			Sleep(1000)
			MouseClick("left", 235, 75, 1, 0)
			Sleep(1000)
			MouseClick("left", 1013, 8, 1, 0)
			Local $errorOKControl = WaitForControl("[TITLE:in$]", "", "[CLASS:Button; TEXT:OK]", ${xu.SECOND*3})
			If $errorOKControl Then
				ControlClick("[TITLE:in$]", "", "[CLASS:Button; TEXT:OK]")
			EndIf
			Sleep(5000)

			; Program tends to hang forever preventing any other instances from running, so we kill this process which kills the program
			ProcessClose("ntvdm.exe")`
	});
	renameOut = false;
}
