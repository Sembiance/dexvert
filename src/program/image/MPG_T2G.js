import {Program} from "../../Program.js";

export class MPG_T2G extends Program
{
	website  = "https://archive.org/details/t425l1e_zip";
	unsafe   = true;
	loc      = "win2k";
	bin      = "c:\\tscad4\\MPG_T2G.EXE";
	osData   = ({
		script : `
			$mainWindowVisible = WinWaitActive("[CLASS:ConvertWClass]", "", 5)
			If $mainWindowVisible Not = 0 Then
				Send("{F2}")

				$exportVisible = WinWaitActive("[TITLE:Select source file]", "", 10)
				If $exportVisible Not = 0 Then
					Sleep(500)
					MouseClick("left", 462, 390, 1, 0)
					Sleep(500)
					Send("in.mpg{ENTER}")
					WinWaitClose("[TITLE:Select source file]", "", 10)
				EndIf

				$exportVisible = WinWaitActive("[TITLE:Select target file]", "", 10)
				If $exportVisible Not = 0 Then
					Sleep(500)
					MouseClick("left", 467, 430, 1, 0)
					Sleep(500)
					Send("out.t2g{ENTER}")
					WinWaitClose("[TITLE:Select target file]", "", 10)
				EndIf

				Sleep(500)
				SendSlow("!fx")

				WinWaitClose("[CLASS:ConvertWClass]", "", 10)
			EndIf`});
	renameOut = true;
	chain     = "T2G_T3G";
}
