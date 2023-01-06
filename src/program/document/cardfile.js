import {Program} from "../../Program.js";

export class cardfile extends Program
{
	website  = "http://www.geert.com/CardFile.htm";
	unsafe   = true;
	loc      = "win2k";
	bin      = "cardfile.exe";
	args     = r => [r.inFile()];
	qemuData = ({
		script : `
			$mainWindowVisible = WinWaitActive("[CLASS:TMain_Form]", "", 7)
			If $mainWindowVisible = 0 Then
				$errorVisible = WinWaitActive("[TITLE:CardFile by GEERT.COM]", "", 7)
				If $errorVisible Not = 0 Then
					ControlClick("[TITLE:CardFile by GEERT.COM]", "", "[CLASS:Button; TEXT:OK]")
				EndIf

				WinWaitActive("[CLASS:TMain_Form]", "", 7)
			Else
				Send("^p")

				WinWaitActive("[CLASS:TMessageForm; TITLE:Information]", "", 30)

				ControlClick("[CLASS:TMessageForm; TITLE:Information]", "", "[CLASS:TButton; TEXT:OK]")
				FileWrite("c:\\out\\out.txt", ClipGet())
			EndIf

			SendSlow("!fx")`
	});
	renameOut = true;
}
