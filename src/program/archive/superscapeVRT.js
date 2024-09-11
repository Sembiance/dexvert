import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class superscapeVRT extends Program
{
	website  = "https://archive.superscape.org/Software/VRT/VRT_5.60.0.4112.iso";
	loc      = "win2k";
	bin      = "c:\\Program Files\\Superscape\\VRT\\WVRT.exe";
	args     = r => [r.inFile()];
	osData   = r => ({
		script : `
			Local $mainWindowActive = 0
			; The file information window doesn't always appear, but if it does, it's not always the 'active' window and so we need to click it to dismiss it
			Func WaitForFileInfo()
				WindowFailure("", "Erroring Decompressing", -1, "{ENTER}")
				WindowFailure("", "ERROR: Configuration file", -1, "{ENTER}")
				WindowFailure("", "Failed to create empty document", -1, "{ENTER}")
				If WinActive("${path.basename(r.inFile())} - Superscape VRT", "") Then
					$mainWindowActive = 1
					return 1
				EndIf
				return WinExists("File Information", "")
			EndFunc
			$fileInfoWindow = CallUntil("WaitForFileInfo", ${xu.SECOND*30})
			If Not $mainWindowActive Then
				Sleep(1000)
				MouseClick("left", 40, 40)
				Send("{ENTER}")
				WinWaitClose($fileInfoWindow, "", 10)
			EndIf

			$mainWindow = WindowRequire("${path.basename(r.inFile())} - Superscape VRT", "", 10)

			WindowFailure("VRT - Error", "Access prohibited", 2, "{ESCAPE}")

			; VRML
			Send("!f")
			SendSlow("ie")
			WindowDismiss("VRML Export Options", "", "{ENTER}")
			$exportVRMLWindow = WindowRequire("Export VRML File", "", 10)
			Send("c:\\out\\world.wrl{ENTER}")
			WinWaitClose($exportVRMLWindow, "", 10)
			$exportProgressWindow = WinWaitActive("Export VRML", "", 4)
			If $exportProgressWindow Then
				WinWaitClose($exportProgressWindow, "", 240)
			EndIf
			WaitForStableFileSize("c:\\out\\world.wrl", ${xu.SECOND*3}, ${xu.SECOND*25})

			; Script
			Send("!e")
			SendSlow("sw")
			AutoItSetOption("WinTitleMatchMode", 2)
			$editWorldWindow = WindowRequire("Edit World", "", 60)
			AutoItSetOption("WinTitleMatchMode", 1)
			ClipPut("")
			Send("^a")
			Sleep(${xu.SECOND*2})
			Send("^c")
			WaitForClipChange(${xu.SECOND*5})
			FileWrite("c:\\out\\world.script", ClipGet())
			Send("{ESCAPE}")
			WinWaitClose($editWorldWindow, "", 5)

			; Shape
			Send("!r")
			Send("s")
			Func WaitForShapeWindow()
				return ControlGetText($mainWindow, "", "[CLASS:Static; INSTANCE:21]") == "SHAPE"
			EndFunc
			If CallUntil("WaitForShapeWindow", ${xu.SECOND*5}) Then
				Send("!e")
				SendSlow("ss")
				AutoItSetOption("WinTitleMatchMode", 2)
				$editShapeScriptWindow = WindowRequire("Edit Shape", "", 60)
				AutoItSetOption("WinTitleMatchMode", 1)
				
				ClipPut("")
				Send("^a")
				Sleep(${xu.SECOND*2})
				Send("^c")
				WaitForClipChange(${xu.SECOND*5})
				FileWrite("c:\\out\\shape.script", ClipGet())
				Send("{ESCAPE}")
				WinWaitClose($editShapeScriptWindow, "", 5)
			EndIf

			; Image
			Send("!r")
			Send("i")

			Func WaitForImageWindow()
				return ControlGetText($mainWindow, "", "[CLASS:Static; INSTANCE:31]") == "IMAGE"
			EndFunc
			Local $firstImageNum = 0
			Func ExportImage($canBeFirst)
				; AutoIt scripting is very basic and I can't just combine these methods into like 1 line, sigh
				$imageNumFullRaw = ControlGetText($mainWindow, "", "[CLASS:Static; INSTANCE:30]")
				$imageNumFullTrimmed = StringStripWS($imageNumFullRaw, 7)
				$imageNumParts =  StringSplit($imageNumFullTrimmed, " ")
				$imageNum = Number($imageNumParts[2])
				If $canBeFirst Then
					$firstImageNum = $imageNum
				EndIf
				If $imageNum = $firstImageNum And Not $canBeFirst Then
					return 0
				EndIf
				$fileName = $imageNum
				$imageNameFullRaw = ControlGetText($mainWindow, "", "[CLASS:Static; INSTANCE:32]")
				$imageNameFullTrimmed = StringStripWS($imageNameFullRaw, 7)
				If Not (StringLeft($imageNameFullTrimmed, 5) == "Image") Then
					$fileName = $imageNum & "_" & $imageNameFullTrimmed
				EndIf
				Send("!f")
				SendSlow("ie")
				$saveImageWindow = WindowRequire("Save as Picture", "", 5)
				Send("c:\\out\\" & $fileName & ".pcx{ENTER}")
				WinWaitClose($saveImageWindow, "", 5)
				WinWaitActive($mainWindow, "", 5)
				Send("!i")
				Send("n")
				return 1
			EndFunc
			If CallUntil("WaitForImageWindow", ${xu.SECOND*5}) And Not (ControlGetText($mainWindow, "", "[CLASS:Static; INSTANCE:30]") == "No Images")  Then
				Local $ret = 0
				Do
					$ret = ExportImage($ret = 0)
				Until $ret = 0
			EndIf

			; Sound
			Send("!r")
			Send("n")
			Func WaitForSoundWindow()
				return ControlGetText($mainWindow, "", "[CLASS:Static; INSTANCE:42]") == "SOUND"
			EndFunc
			If CallUntil("WaitForSoundWindow", ${xu.SECOND*5}) And Not (ControlGetText($mainWindow, "", "[CLASS:Static; INSTANCE:41]") == "No Sounds")  Then
				Send("!f")
				SendSlow("fa")
				$saveSoundWindow = WindowRequire("Save Sound File", "", 5)
				Send("c:\\out\\world.snd{ENTER}")
				WinWaitClose($saveSoundWindow, "", 5)
			EndIf
			
			Send("!f")
			Send("x")
			WinWaitClose($mainWindow, "", 5)`
	});
	renameOut = false;
	chain = "?nconvert";
	chainCheck = (r, chainFile) => chainFile.ext.toLowerCase()===".pcx";
}
