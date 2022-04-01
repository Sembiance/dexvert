import {Program} from "../../Program.js";

export class T2G_T3G extends Program
{
	website  = "https://archive.org/details/t425l1e_zip";
	unsafe   = true;
	loc      = "win2k";
	bin      = "c:\\tscad4\\T2G_T3G.EXE";
	qemuData = ({
		script : `
			$mainWindowVisible = WinWaitActive("[CLASS:ConvertWClass]", "", 5)
			If $mainWindowVisible Not = 0 Then
				Send("{F2}")

				$exportVisible = WinWaitActive("[TITLE:Select source file]", "", 10)
				If $exportVisible Not = 0 Then
					Sleep(500)
					MouseClick("left", 462, 379, 2, 0)
					Sleep(500)
					MouseClick("left", 298, 331, 2, 0)
					WinWaitClose("[TITLE:Select source file]", "", 10)
				EndIf

				$exportVisible = WinWaitActive("[TITLE:Select target file]", "", 10)
				If $exportVisible Not = 0 Then
					Sleep(500)
					MouseClick("left", 467, 416, 2, 0)
					Sleep(500)
					Send("out.t3g{ENTER}")
					WinWaitClose("[TITLE:Select target file]", "", 10)
				EndIf

				Sleep(500)
				Send("!f")
				Sleep(100)
				Send("x")
				Sleep(100)

				WinWaitClose("[CLASS:ConvertWClass]", "", 10)
			EndIf`});
	renameOut = true;
	chain     = "T3G_T4G";
}
