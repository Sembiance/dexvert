import {xu} from "xu";
import {Program} from "../../Program.js";

export class printArtist extends Program
{
	website  = "https://winworldpc.com/product/instant-artist-print/60";
	loc      = "win2k";
	bin      = "c:\\dexvert\\SIERRA\\PA6\\PRTARTST.EXE";
	qemuData = ({
		alsoKill  : ["ntvdm.exe"],
		script : `
			#include <GuiListBox.au3>
			
			$mainWindow = WindowRequire("Print Artist", "", 5)

			Send("{ESCAPE}^n")
			$newWindow = WindowRequire("Select New Scrapbook", "", 5)
			Send("{HOME}{ENTER}")
			WinWaitClose($newWindow, "", 3)
			WinWaitActive($mainWindow, "", 3)

			Send("^g")

			$insertWindow = WindowRequire("Graphics Grabber", "", 5)

			Local $graphicListHandle = WaitForControl($insertWindow, "", "[CLASS:ListBox; INSTANCE:1]", ${xu.SECOND*5})
			If $graphicListHandle = 0 Then
				Exit 0
			EndIf

			Local $graphicCount = _GUICtrlListBox_GetCount($graphicListHandle)
			If $graphicCount = 0 Then
				Exit 0
			EndIf

			For $graphicNum = 0 To $graphicCount-1 Step 1
				SendSlow("^c{TAB}{ENTER}")
				WinWaitClose($insertWindow, "", 3)
				WinWaitActive($mainWindow, "", 3)
				
				; allow time for the graphic to render
				Sleep(3000)
				
				Send("^e")
				$exportWindow = WindowRequire("Export Object", "", 5)
				If $graphicNum = 0 Then
					Send("{TAB}{TAB}{HOME}p+{TAB}+{TAB}")
				EndIf
				$numberedFilename = "c:\\out\\out" & $graphicNum & ".eps"
				Send($numberedFilename & "+{TAB}+{TAB}+{TAB}{ENTER}");
				WinWaitClose($exportWindow, "", 3)
				WinWaitActive($mainWindow, "", 3)
				Send("{DELETE}^g")
				$insertWindow = WindowRequire("Graphics Grabber", "", 5)
				If $graphicCount-$graphicNum > 1 Then
					SendSlow("{TAB}{DOWN}+{TAB}", 500)
				EndIf
				FileMove($numberedFilename, "c:\\out\\" & StringRegExpReplace(StringRegExpReplace(ClipGet(), '[^a-zA-Z0-9 _-]', ''), "  ", " ") & ".eps")
			Next

			SendSlow("{ESCAPE}^fx")

			Func PostExitWindows()
				WindowDismiss("[TITLE:Print Artist]", "Save changes", "n")
			EndFunc
			CallUntil("PostExitWindows", ${xu.SECOND*3})`
	});
	renameOut = false;
	chain = "ps2pdf[fromEPS][svg]";
}
