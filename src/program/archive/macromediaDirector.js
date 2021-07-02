"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website : "https://www.buraks.com/swifty/xena.html"
};

exports.qemu = () => "c:\\Program Files\\Macromedia\\Director MX 2004\\Director.exe";
exports.args = (state, p, r, inPath=state.input.filePath) => [inPath];
exports.qemuData = (state, p, r) =>
{
	const data = {	// eslint-disable-line sembiance/no-useless-variables
		inFilePaths  : [r.args[0]],
		osid         : "winxp",
		script       : `
			#include <GuiListView.au3>

			WinWaitActive("[TITLE:Director MX 2004]", "", 10)

			;Wait for the 'Cast' sub window/control to appear
			WaitForControl("[TITLE:Director MX 2004]", "", "[CLASS:ASISubWndClass; TEXT:Untitled: Cast]", ${XU.SECOND*10}, "[TITLE:Error]", "[CLASS:Button; TEXT:OK]", "[TITLE:Locate replacement]")

			; Wait for the list of cast items to appear
			Local $castListHandle = WaitForControl("[TITLE:Director MX 2004]", "", "[CLASS:SysListView32; INSTANCE:5]", ${XU.SECOND*30})

			Sleep(500)

			Local $castCount = _GUICtrlListView_GetItemCount($castListHandle)

			; NOTE: Text is actual rich, but we lose all formatting because we just copy it into the clipboard and write that to a file
			Func HandleText($itemNum, $filename)
				Send("{Enter}")
				Local $textControl = WaitForControl("[TITLE:Director MX 2004]", "", "[CLASS:ASISubWndClass; TEXT:Untitled: Text]", ${XU.SECOND*2})
				Send("^a")
				Send("^c")
				WaitForClipChange(${XU.SECOND})
				FileWrite("c:\\out\\" & $filename & ".txt", ClipGet())
				Send("^{F4}")
			EndFunc

			; Utilizes COPYFILE.exe (which was compiled from COPYFILE.AU3 using Aut2Exe) which copies the file to out
			Func HandleExport($itemNum, $filename)
				ClipPut($filename)
				Send("^,")
				Local $exportControl = WaitForControl("[CLASS:MMDialogWndClass]", "", "[CLASS:Button; TEXT:Cancel]", ${XU.SECOND*3}, "[TITLE:Director]", "[CLASS:Button; TEXT:OK]")
				If $exportControl Then
					ProcessWaitClose("COPYFILE.exe", ${XU.SECOND*10})
					ControlClick("[CLASS:MMDialogWndClass]", "", "[CLASS:Button; TEXT:Cancel]")
					WinWaitClose("[CLASS:MMDialogWndClass]", "", ${XU.SECOND*3})
				EndIf
				ControlFocus("[TITLE:Director MX 2004]", "", $castListHandle)
			EndFunc

			Func HandleIgnored()
			EndFunc

			Func HandleUnsupported($itemNum, $filename)
				FileWrite("c:\\out\\" & $filename & "_UNSUPPORTED", "Unhandled cast type. Details:" & @LF & _GUICtrlListView_GetItemTextString($castListHandle, $itemNum) & @LF)
			EndFunc

			Func HandleUnknown($itemNum, $filename)
				FileWrite("c:\\out\\" & $filename & "_UNKONWN", "Unhandled cast type. Details:" & @LF & _GUICtrlListView_GetItemTextString($castListHandle, $itemNum) & @LF)
			EndFunc

			Send("{HOME}")

			;For $itemNum = 0 To 5 Step 1
			For $itemNum = 0 To $castCount-1 Step 1
				Local $itemName = _GUICtrlListView_GetItemText($castListHandle, $itemNum, 0)
				Local $itemid = _GUICtrlListView_GetItemText($castListHandle, $itemNum, 1)
				Local $subtype = _GUICtrlListView_GetItemText($castListHandle, $itemNum, 3)
				Local $type = _GUICtrlListView_GetItemText($castListHandle, $itemNum, 4)
				Local $filename = StringFormat("%05u", Number($itemid)) & "_" & $type & "_" & $itemName
				Switch $type
					Case "Text"
						HandleText($itemNum, $filename)
					Case "Field"
						HandleText($itemNum, $filename)
					Case "Script"
						HandleExport($itemNum, $filename)
					Case "Bitmap"
						HandleExport($itemNum, $filename)
					Case "Shape"
						HandleIgnored()
					Case "Button"
						HandleIgnored()
					Case "QuickTime"
						HandleIgnored()
					Case Else
						HandleUnknown($itemNum, $filename)
				EndSwitch

				Send("{DOWN}")
			Next

			Send("!fx")

			WaitForPID(ProcessExists("Director.exe"), ${XU.MINUTE*10})`
	};

	// NOTE!! Even though we actually copy over the xtras directory into WinXP, we DO NOT actually put the files where they need to go to function:
	// C:\Program Files\Macromedia\Director MX 2004\Configuration\Xtras
	// This is because if there are any duplicate files (which is almost always the case) then director won't launch correctly until those are removed
	// So we would have to prune out any custom xtras from ones we already have on windows. We in theory could do that linux side before it gets in by just pre-generating hash sums of all files that ship default with director
	// But meh. This seems like a lot of work for potentially no payoff. Like how would we even know how to 'handle' an xtra format anyways? We would have to add custom handling code, meh.
	//const xtrasFilename = (state.extraFilenames || []).find(v => v.toLowerCase()==="xtras");
	//if(xtrasFilename)
	//	data.inFilePaths.push(xtrasFilename);

	return data;
};
