import {Program} from "../../Program.js";

export class frameMaker extends Program
{
	website  = "https://winworldpc.com/product/framemaker/50";
	unsafe   = true;
	loc      = "win2k";
	bin      = "c:\\MAKER5\\FRAME.EXE";
	args     = r => [r.inFile()];
	qemuData = ({
		script : `
			$noPrinterWin = WinWaitActive("FrameMaker", "Can't find a compatible default printer", 5)
			If $noPrinterWin Not = 0 Then
				ControlClick("FrameMaker", "Can't find a compatible default printer", "[CLASS:Button; TEXT:OK]")

				$oldDocWin = WinWaitActive("FrameMaker", "will be converted to the current release", 5)
				If $oldDocWin Not = 0 Then
					ControlClick("FrameMaker", "will be converted to the current release", "[CLASS:Button; TEXT:OK]")
				EndIf

				$missingFontWin = WinWaitActive("FrameMaker", "unavailable font", 5)
				If $missingFontWin Not = 0 Then
					ControlClick("FrameMaker", "unavailable font", "[CLASS:Button; TEXT:OK]")
				EndIf

				$missingLanguageWin = WinWaitActive("FrameMaker", "unavailable language", 5)
				If $missingLanguageWin Not = 0 Then
					ControlClick("FrameMaker", "unavailable language", "[CLASS:Button; TEXT:OK]")
				EndIf

				$missingFileWin = WinWaitActive("Missing File", "", 5)
				If $missingFileWin Not = 0 Then
					Send("{TAB}{TAB}{TAB}{TAB}{TAB}{DOWN}{DOWN}{ENTER}")
					WinWaitClose("Missing File", "", 5)
				EndIf

				Local $errorWin
				Do
					Sleep(500)

					$errorWin = WinActive("FrameMaker", "does not exist")
					If $errorWin Not = 0 Then
						ControlClick("FrameMaker", "does not exist", "[CLASS:Button; TEXT:OK]")
					EndIf

					$errorWin = WinActive("FrameMaker", "Cannot display")
					If $errorWin Not = 0 Then
						ControlClick("FrameMaker", "Cannot display", "[CLASS:Button; TEXT:OK]")
					EndIf					

					Sleep(1000)
				Until $errorWin = 0

				WinWaitActive("FrameMaker", "", 5)
								
				Sleep(1000)
				Send("!f")
				Sleep(250)
				Send("a")

				WinWaitActive("Save Document", "", 5)

				Send("c:\\out\\out.rtf{TAB}{TAB}{TAB}{TAB}{TAB}r{ENTER}")

				WinWaitClose("Save Document", "", 5)

				Send("!f")
				Sleep(250)
				Send("x")

				$unsavedWin = WinWaitActive("FrameMaker", "Unsaved", 5)
				If $unsavedWin Not = 0 Then
					ControlClick("FrameMaker", "Unsaved", "[CLASS:Button; TEXT:&No]")
				EndIf
			EndIf`
	});
	chain     = "dexvert[asFormat:document/rtf]";
	renameOut = true;
}
