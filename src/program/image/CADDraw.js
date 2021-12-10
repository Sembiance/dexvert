import {Program} from "../../Program.js";

export class CADDraw extends Program
{
	website  = "https://archive.org/details/t425l1e_zip";
	unsafe   = true;
	loc      = "win2k";
	bin      = "c:\\tscad4\\RELEASE4.EXE";
	args     = r => [r.inFile()];
	qemuData = ({
		script : `
			$mainWindowVisible = WinWaitActive("[CLASS:MainWClassToso4]", "", 5)
			If $mainWindowVisible Not = 0 Then
				Sleep(500)
				Send("!f")
				Sleep(100)
				Send("a")
				Sleep(100)

				$exportVisible = WinWaitActive("[TITLE:Save Drawing as...]", "", 10)
				If $exportVisible Not = 0 Then
					Send("c:\\out\\out.wmf{TAB}w{ENTER}")

					WinWaitClose("Save Drawing as...", "", 10)

					$messageVisible = WinWaitActive("[TITLE:Message]", "", 10)
					If $messageVisible Not = 0 Then
						ControlClick("[TITLE:Message]", "", "[CLASS:Button; TEXT:&Yes]")
						WinWaitClose("Message", "", 10)
					EndIf
				EndIf

				Sleep(500)
				Send("!f")
				Sleep(100)
				Send("x")
				Sleep(100)

				WinWaitClose("[CLASS:MainWClassToso4]", "", 10)
			EndIf`});
	renameOut = true;
	chain     = "dexvert[asFormat:image/wmf]";
}
