import {Program} from "../../Program.js";

export class Fony extends Program
{
	website  = "http://hukka.ncn.fi/?fony";
	loc      = "win2k";
	bin      = "Fony.exe";
	args     = r => [r.inFile()];
	qemuData = ({
		quoteArgs : true,
		script : `
			$errorVisible = WinWaitActive("[TITLE:Error Loading Font]", "", 5)
			If $errorVisible Not = 0 Then
				ControlClick("[TITLE:Error Loading Font]", "", "[CLASS:TBitBtn; TEXT:OK]")
			Else
				WinWaitActive("[CLASS:TFMain]", "", 30)
				Sleep(1000)
				SendSlow("!fe{DOWN}{ENTER}")

				$exportVisible = WinWaitActive("[CLASS:TFBDFExport; TITLE:BDF Export]", "", 7)
				If $exportVisible Not = 0 Then
					ControlClick("[CLASS:TFBDFExport]", "", "[CLASS:TButton; TEXT:OK]")

					WinWaitActive("[TITLE:Save As]", "", 30)
					ControlClick("[TITLE:Save As]", "", "[CLASS:Edit]")

					Send("{HOME}c:\\out\\")
					ControlClick("[TITLE:Save As]", "", "[CLASS:Button; TEXT:&Save]")

					WinWaitActive("[CLASS:TFMain]", "", 30)
					Sleep(200)
				EndIf

				SendSlow("!fx")
			EndIf`
	});
	renameOut = true;
	chain = "dexvert[asFormat:font/bdf]";
}
