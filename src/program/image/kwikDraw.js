import {Program} from "../../Program.js";

export class kwikDraw extends Program
{
	website  = "https://github.com/Sembiance/dexvert/blob/master/os/aux/winxp/app/KDRAW140.ZIP";
	loc      = "winxp";
	unsafe   = true;
	bin      = "C:\\dexvert\\KDRAW_FW.EXE";
	args     = r => [r.inFile()];
	osData   = ({
		script : `
			WindowRequire("KWIKDRAW", "This is a Freeware", 2)
			ControlClick("KWIKDRAW", "This is a Freeware", "[CLASS:Button; TEXT:OK]")
			WinWaitClose("KWIKDRAW", "This is a Freeware", 10)
			WindowFailure("KWIKDRAW", "NOT a Valid KwikDraw File", 2, "{ENTER}")
			$convertWindow = WinWaitActive("KWIKDRAW", "Converting", 3)
			If $convertWindow Not = 0 Then
				ControlClick("KWIKDRAW", "Converting", "[CLASS:Button; TEXT:OK]")
				WinWaitClose("KWIKDRAW", "Converting", 5)
			EndIf
			WinWaitActive("[CLASS:KWIKDRAW]", "", 10)
			SendSlow("!fp")
			WinWaitActive("PRINT", "", 10)
			ControlClick("PRINT", "", "[CLASS:Button; TEXT:Print]")
			WinWaitActive("Print to File", "", 10)
			Send("c:\\out\\out.ps{ENTER}")
			WinWaitClose("Print to File", "", 10)
			Sleep(5000)
			WinWaitActive("[CLASS:KWIKDRAW]", "", 10)
			SendSlow("!fx")`
	});
	renameOut = true;
	chain     = "ps2pdf[svg]";
}
