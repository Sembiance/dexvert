import {Program} from "../../Program.js";

export class T3G_T4G extends Program
{
	website  = "https://archive.org/details/t425l1e_zip";
	unsafe   = true;
	loc      = "win2k";
	bin      = "c:\\tscad4\\T3G_T4G.EXE";
	args     = r => [r.inFile()];
	osData   = ({
		script : `
			$mainWindowVisible = WinWaitActive("[CLASS:ConvertWClass]", "", 5)
			If $mainWindowVisible Not = 0 Then
				Send("{F2}")

				$exportVisible = WinWaitActive("[TITLE:Select source file]", "", 10)
				If $exportVisible Not = 0 Then
					Send("c:\\in{ENTER}")
					Sleep(200)
					Send("{TAB}{DOWN}{ENTER}")
					WinWaitClose("[TITLE:Select source file]", "", 10)
				EndIf

				$exportVisible = WinWaitActive("[TITLE:Select target file]", "", 10)
				If $exportVisible Not = 0 Then
					Send("c:\\out{ENTER}")
					Sleep(200)
					Send("out.t4g{ENTER}")
					WinWaitClose("[TITLE:Select target file]", "", 10)
				EndIf

				Sleep(500)
				SendSlow("!fx")

				WinWaitClose("[CLASS:ConvertWClass]", "", 10)
			EndIf`});
	renameOut = true;
	chain     = "CADDraw";
}
