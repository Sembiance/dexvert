import {Program} from "../../Program.js";

export class kwikDraw130 extends Program
{
	website = "https://github.com/Sembiance/dexvert/blob/master/os/aux/winxp/app/KDRAW130.EXE";
	loc     = "win7";
	unsafe  = true;
	bin     = "C:\\dexvert\\KDRAW130.EXE";
	osData  = ({
		script : `
			$freewareWindow = WindowRequire("KWIKDRAW", "This is a Freeware", 5)
			ControlClick($freewareWindow, "", "[CLASS:Button; TEXT:OK]")
			WinWaitClose($freewareWindow, "", 10)
			SendSlow("{LALT}{DOWN}o")

			$openWindow = WindowRequire("OPEN", "", 5)
			SendSlow("{TAB}{DOWN}{ENTER}")
			WinWaitClose($freewareWindow, "", 10)
			
			Sleep(1000)
			WindowFailure("", "NOT a Valid KwikDraw File", -1, "{ENTER}")

			SendSlow("{LALT}{DOWN}p")
			$printWindow = WindowRequire("PRINT", "", 5)
			Send("{ENTER}")
			WinWaitClose($printWindow, "", 10)

			HandleCutePDFPrint()

			WinWaitActive("[CLASS:KWIKDRAW]", "", 10)
			SendSlow("{LALT}{DOWN}x")`
	});
	renameOut = true;
	chain     = "ps2pdf[svg]";
}
