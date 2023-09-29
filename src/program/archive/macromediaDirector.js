import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class macromediaDirector extends Program
{
	website  = "https://www.buraks.com/swifty/xena.html";
	loc      = "winxp";
	bin      = "c:\\Program Files\\Macromedia\\Director MX 2004\\Director.exe";
	//args     = r => [r.inFile()];	// Director DOES support opening the file directly by passing it as an arg, but then we don't get a chance to first "Enable" our movie restorer Xtra
	notes    = "Sometimes a file can fail to copy over if there is severe CPU load on the host system. Adding more delays would slow down extraction too much. Adding logic to check that things are ready is probably the best approach, but meh.";

	// NOTE!! We don't do anything with aux files like other Xtras distributed with the files
	// C:\Program Files\Macromedia\Director MX 2004\Configuration\Xtras
	// This is because if there are any duplicate files (which is almost always the case) then director won't launch correctly until those are removed
	// So we would have to prune out any custom xtras from ones we already have on windows. We in theory could do that linux side before it gets in by just pre-generating hash sums of all files that ship default with director
	// But meh. This seems like a lot of work for potentially no payoff. Like how would we even know how to 'handle' an xtra format anyways? We would have to add custom handling code, meh.

	osData = r => ({
		script : `
			#include <GuiListView.au3>

			Opt("WinTitleMatchMode", 2)

			WinWaitActive("Director MX 2004", "", 10)

			; Enable out Movie Restorer XTra
			Send("!x{UP}{UP}{RIGHT}{ENTER}")
			WinWaitActive("", "Movie Restorer Tool Enabled Successfully", 10)
			Send("{ENTER}")

			Sleep(200)

			Send("^o")
			WinWaitActive("Open", "", 10)
			Sleep(200)
			Send("c:\\in\\${path.basename(r.inFile())}{ENTER}")

			; Wait for long running font building
			Func FontBuilding()
				WinWaitClose("Font Progress", "", 40)
			EndFunc
			CallUntil("FontBuilding", ${xu.SECOND*3})

			; Dismiss Player Errors and missing fonts
			Func DismissWarnings()
				WinWaitClose("Font Progress", "", 30)
				WindowDismiss("[TITLE:Error]", "", "{ENTER}")
				WindowDismiss("Locate replacement", "", "{ESCAPE}")
				WindowDismiss("Where is", "", "{ESCAPE}")
				WindowDismiss("Director Player Error", "", "{ENTER}")
				WindowDismiss("Missing Fonts", "", "{ENTER}")
			EndFunc
			CallUntil("DismissWarnings", ${xu.SECOND*3})

			${r.inFile().toLowerCase().endsWith(".dir") ? `
			SendSlow("^4^4")
			` : ""}

			; Wait for the 'Cast' sub window/control to appear
			WaitForControl("Director MX 2004", "", "[CLASS:ASISubWndClass]", ${xu.SECOND*10})

			; Wait for the list of cast items to appear
			Local $castListHandle = WaitForControl("Director MX 2004", "", "[CLASS:SysListView32; INSTANCE:5]", ${xu.SECOND*30})

			Sleep(500)

			Local $castCount = _GUICtrlListView_GetItemCount($castListHandle)

			; NOTE: Text is actual rich, but we lose all formatting because we just copy it into the clipboard and write that to a file
			Func HandleText($itemNum, $filename)
				Send("{Enter}")
				Local $textControl = WaitForControl("Director MX 2004", "", "[CLASS:ASISubWndClass; TEXT:Untitled: Text]", ${xu.SECOND*2})
				Sleep(200)
				Send("^a")
				Sleep(50)
				Send("^c")
				WaitForClipChange(${xu.SECOND})
				FileWrite("c:\\out\\" & $filename & ".txt", ClipGet())
				Send("^{F4}")
			EndFunc

			; Utilizes COPYFILE.exe (which was compiled from COPYFILE.AU3 using Aut2Exe) which copies the file to out
			Func HandleExport($itemNum, $filename)
				ClipPut($filename)
				Send("^,")
				Local $exportControl = WaitForControl("[CLASS:MMDialogWndClass]", "", "[CLASS:Button; TEXT:Cancel]", ${xu.SECOND*3}, "[TITLE:Director]", "[CLASS:Button; TEXT:OK]")
				If $exportControl Then
					ProcessWaitClose("COPYFILE.exe", ${xu.SECOND*10})
					ControlClick("[CLASS:MMDialogWndClass]", "", "[CLASS:Button; TEXT:Cancel]")
					WinWaitClose("[CLASS:MMDialogWndClass]", "", ${xu.SECOND*3})
				EndIf
				ControlFocus("Director MX 2004", "", $castListHandle)
			EndFunc

			Func HandleIgnored($itemNum, $filename)
				FileWrite("c:\\out\\" & $filename & "_DEXIGNORED", "Ignored cast type. Details:" & @LF & _GUICtrlListView_GetItemTextString($castListHandle, $itemNum) & @LF)
			EndFunc

			Func HandleUnsupported($itemNum, $filename)
				FileWrite("c:\\out\\" & $filename & "_DEXUNSUPPORTED", "Unhandled cast type. Details:" & @LF & _GUICtrlListView_GetItemTextString($castListHandle, $itemNum) & @LF)
			EndFunc

			Func HandleUnknown($itemNum, $filename)
				FileWrite("c:\\out\\" & $filename & "_DEXUNKONWN", "Unhandled cast type. Details:" & @LF & _GUICtrlListView_GetItemTextString($castListHandle, $itemNum) & @LF)
			EndFunc

			Send("{HOME}")
			Sleep(500)
			Send("{HOME}")

			;For $itemNum = 0 To 5 Step 1
			For $itemNum = 0 To $castCount-1 Step 1
				Local $itemName = StringReplace(StringReplace(_GUICtrlListView_GetItemText($castListHandle, $itemNum, 0), "/", "-"), "\\", "-")
				Local $itemid = _GUICtrlListView_GetItemText($castListHandle, $itemNum, 1)
				Local $subtype = _GUICtrlListView_GetItemText($castListHandle, $itemNum, 3)
				Local $type = _GUICtrlListView_GetItemText($castListHandle, $itemNum, 4)
				Local $filename = StringFormat("%05u", Number($itemid)) & "_" & $type & "_" & $itemName
				Switch $type
					; TEXT items
					Case "Text"
						HandleText($itemNum, $filename)
					Case "Field"
						HandleText($itemNum, $filename)
					
					; EXPORTABLE items
					Case "Script"
						HandleExport($itemNum, $filename)
					Case "Bitmap"
						HandleExport($itemNum, $filename)
					Case "Sound"
						HandleExport($itemNum, $filename)

					; IGNORED items
					Case "Shape"
						HandleIgnored($itemNum, $filename)
					Case "Button"
						HandleIgnored($itemNum, $filename)
					Case "Transition"
						HandleIgnored($itemNum, $filename)
					Case "QuickTime"
						HandleIgnored($itemNum, $filename)
					Case "Palette"
						HandleIgnored($itemNum, $filename)
					
					; UNKNOWN
					Case Else
						HandleUnknown($itemNum, $filename)
				EndSwitch

				Send("{DOWN}")
			Next

			SendSlow("!fx")

			Local $saveChangesVisible = WinWaitActive("[TITLE:Director]", "", 3)
			If $saveChangesVisible Not = 0 Then
				ControlClick("[TITLE:Director]", "", "[CLASS:Button; TEXT:&No]")
			EndIf`
	});

	// Often SCRIPT files are just behaviors and end up being just 1 single empty byte in size, just delete these, they are not useful
	verify = (r, dexFile) =>
	{
		r.processed = true;	// explicitly state that we have processed this file and are done
		return dexFile.size>1 && !dexFile.base.toLowerCase().endsWith("_dexignored");
	};

	renameOut = false;
}
