import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";
import {fileUtil} from "xutil";

export class shockwave3DWorldConverter extends Program
{
	website   = "https://github.com/tomysshadow/Shockwave-3D-World-Converter";
	loc       = "wine";
	bin       = "Shockwave-3D-World-Converter/Shockwave3DWorldConverter.exe";
	exclusive = "wine";
	args      = r => [`c:\\in${r.wineCounter}\\${path.basename(r.inFile())}`];
	wineData  = {
		script : `
		; ALL OF THIS BELOW IS A DISASTER OF FAILED ATTEMPTS
		#include <FileConstants.au3>

		$mainWindow = WindowRequire("Shockwave 3D World Converter 1.3.9", "", 10)
		Sleep(5000)

		$scriptFile = FileOpen("c:\\dexvert\\sw3d.ahk", $FO_OVERWRITE)
		FileWriteLine($scriptFile, "WinGetPos, X, Y, Width, Height, Shockwave 3D World Converter 1.3.9")
		FileWriteLine($scriptFile, "TargetX := X + 300")
		FileWriteLine($scriptFile, "TargetY := Y + 335")
		FileWriteLine($scriptFile, "MouseMove, TargetX, TargetY, 0")
		FileWriteLine($scriptFile, "Click")
		FileClose($scriptFile)

		RunWait("c:\\Program Files\\AutoHotKey\\AutoHotKey.exe c:\\dexvert\\sw3d.ahk")



		; get our position and send click to top left + x:200 y:300
		;$pos = WinGetPos($mainWindow)
		;MouseClick("left", $pos[0]+300, $pos[1]+335, 1, 0)

		
		;Send("{CTRLDOWN}")
		;Send("e")
		;Send("{CTRLUP}")
		;SendKeepActive($mainWindow, "")
		;Sleep(3000)
		
		;$errorWindow = WinGetHandle("Director Player Error", "")
		;If $errorWindow Not= 0 Then
		;	WinActivate($errorWindow)
		;	Send("y")
		;	Sleep(500)
		;	Send("y")
		;	Sleep(500)
		;	Send("y")
		;EndIf
		;SendSlow("{TAB}{TAB}y")
		;Send("y")

		;Func SaveSaveDialogOrErrors()
		;	WindowDismiss("Director Player Error", "", "{TAB}{TAB}{ENTER}")
		;	return WinGetHandle("Export Wavefront OBJ File...", "")
		;EndFunc
		;$saveWindow = CallUntil("DismissPreSaveWarnings", ${xu.MINUTE})

		;Sleep(30000)
		;Pause()


		;SendKeepActive($mainWindow, "")
		;$saveWindow = WindowRequire("Export Wavefront OBJ File...", "", 10)

		;Send("c:\\out\\out.obj{ENTER}")
		Pause()
		Func DismissWarnings()
			;WindowDismiss("Locate replacement", "", "{ESCAPE}")
			;WindowDismiss("Where is", "", "{ESCAPE}")
			WindowDismiss("Director Player Error", "", "y")
			return WinActive("", "Shockwave 3D World Converted Successfully!")
		EndFunc
		CallUntil("DismissWarnings", ${xu.MINUTE*2})`,
		timeout : xu.MINUTE*2
	};
	notes = xu.trim`
		This program is an utter disaster to automate. By far the WORST I've ever encountered.
		It crashes in 86box emulated win2k and winxp.
		It works in wine, but it doesn't properly respond to AutoIt/AutoHotKey keyboard presses, missing several key presses at random.
		I fussing with it for a few hours, and never once got it to export a file via automation.
		It works ok if you manually click everything with the mouse, but AutoIt/AutoHotKey can't properly emulate mouse clicks when running in wine in a virtual Xvfb display.
		So for now this is being shelved.
		The author said they are burnt out on programming and they don't plan to doing anything with this for month.
		As a programmer, I know that months can easily turn into years and then just as easily turn into never.
		They did spend a little bit of time to add a quick hotkey for export, but even that doesn't work right under automation, only sometimes responding to the hotkey.
		It *might* be possible to load up the source itself in director (see the readme file on github) and compile my own .exe version that works correctly within wine.
		If that works, I could properly ditch the entire 'UI' and just have it export automatically to where I want the output to go.
		I'd still need to respond to Player Errors, which may or may not work, but I could also look at how the awesome n0samu handled auto dismissing errors in their DirectorCastRipper
		But that's just not something I'm gonna bother doing right now.`;
	renameOut  = false;
	chain      = "dexvert[asFormat:poly/wavefrontOBJ]";
	chainCheck = (r, chainFile) => chainFile.ext.toLowerCase()===".obj";
	//chainFailKeep = () => true;
}
