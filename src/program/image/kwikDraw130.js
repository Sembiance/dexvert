import {Program} from "../../Program.js";

export class kwikDraw130 extends Program
{
	website  = "https://github.com/Sembiance/dexvert/blob/master/qemu/winxp/data/app/KDRAW130.EXE";
	loc      = "winxp";
	unsafe   = true;
	bin      = "C:\\dexvert\\KDRAW130.EXE";
	args     = r => [r.inFile()];
	qemuData = ({
		alsoKill : ["ntvdm.exe"],
		script   : `
			WindowRequire("KWIKDRAW", "This is a Freeware", 5)
			ControlClick("KWIKDRAW", "This is a Freeware", "[CLASS:Button; TEXT:OK]")
			WinWaitClose("KWIKDRAW", "This is a Freeware", 10)
			$convertWindow = WinWaitActive("KWIKDRAW", "Converting", 3)
			If $convertWindow Not = 0 Then
				ControlClick("KWIKDRAW", "Converting", "[CLASS:Button; TEXT:OK]")
				WinWaitClose("KWIKDRAW", "Converting", 5)
			EndIf
			WinWaitActive("[CLASS:KWIKDRAW]", "", 10)
			Send("!f")
			Sleep(200)
			Send("p")
			WinWaitActive("PRINT", "", 10)
			ControlClick("PRINT", "", "[CLASS:Button; TEXT:Print]")
			WinWaitActive("Print to File", "", 10)
			Send("c:\\out\\out.ps{ENTER}")
			WinWaitClose("Print to File", "", 10)
			Sleep(5000)
			WinWaitActive("[CLASS:KWIKDRAW]", "", 10)
			Send("!f")
			Sleep(200)
			Send("x")
			Sleep(200)`
	});
	renameOut = true;
	chain     = "ps2pdf -> pdf2svg";
}
