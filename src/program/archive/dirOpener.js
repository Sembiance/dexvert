import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class dirOpener extends Program
{
	website  = "https://www.buraks.com/swifty/xena.html";
	unsafe   = true;
	loc      = "winxp";
	bin      = "dirOpener300-850-1-PC.exe";
	args     = () => [];
	osData   = r => ({
		dontMaximize : true,
		script       : `
			WindowDismissWait("dirOpener300-850-1-PC - No Disk", "", 5, "{ESCAPE}")
			WinWaitActive("dirOpener300-850-1-PC", "", 10)

			; Sometimes dirOpener refuses to save the file to c:\\out and sticks it in C:\\ instead. Sigh.
			$badProjectOutputPath = "c:\\outdirOpened output of in.dir"
			$badCastOutputPath = "c:\\outdirOpened output of in.cst"

			; Check to see if previous leftover files exist, if so delete em
			If FileExists($badProjectOutputPath) Then
				FileDelete($badProjectOutputPath)
			EndIf

			If FileExists($badCastOutputPath) Then
				FileDelete($badCastOutputPath)
			EndIf

			; Sometimes dirOpener chooses to forget all it's preferences, especially the 'Exit After Converting'
			; So we click over to the Preferences tab, reset and then set all the settings the way we want
			Sleep(100)
			MouseClick("left", 321, 221)
			Sleep(100)
			MouseClick("left", 379, 435)
			Sleep(100)
			MouseClick("left", 235, 267)
			Sleep(100)
			MouseClick("left", 236, 309)
			Sleep(100)
			MouseClick("left", 236, 399)
			Sleep(100)
			
			;MouseClick("left", 620, 401)
			;WinWaitActive("Browse for Folder", "", 10)
			;Send("{DOWN}{RIGHT}o{ENTER}")
			;Sleep(500)

			MouseClick("left", 404, 398)
			Sleep(100)
			Send("+{HOME}c:\\out")
			Sleep(100)
			
			MouseClick("left", 469, 434)
			Sleep(1000)

			; Now click Open and being
			MouseClick("left", 255, 440)

			$openWindow = WindowRequire("[TITLE:Select file(s) to open]", "", 10)
			Sleep(200)
			SendSlow("c:\\in\\${path.basename(r.inFile())}{ENTER}")
			WinWaitClose($openWindow, "", 10)

			; Some are missing files and ask "Where is" something
			; Some times errors show up about scripts or other director errors
			; Some files show custom alerts that pop up (pc.dir) some have several in a row
			; They all are the same window class though, so we just use this loop
			Local $alertWindow
			Local $windowOrExitTimer = TimerInit()
			Do
				If Not ProcessExists("dirOpener300-850-1-PC.exe") Then ExitLoop

				$alertWindow = WinWaitActive("[CLASS:#32770]", "", 5)
				If $alertWindow Not = 0 Then
					ControlClick("[CLASS:#32770]", "", "[CLASS:Button; TEXT:OK]")
					ControlClick("[CLASS:#32770]", "", "[CLASS:Button; TEXT:&Yes]")
					ControlClick("[CLASS:#32770]", "", "[CLASS:Button; TEXT:Cancel]")
				EndIf
			Until TimerDiff($windowOrExitTimer) > ${xu.MINUTE*2}

			Sleep(1000)

			; See if it copied to the wrong output and if so, copy it over to c:\\out
			If FileExists($badProjectOutputPath) Then
				FileMove($badProjectOutputPath, "c:\\out\\dexvert.dir")
			EndIf

			If FileExists($badCastOutputPath) Then
				FileMove($badCastOutputPath, "c:\\out\\dexvert.cst")
			EndIf`
	});

	// We rename the file dexvert to ensure we don't collide with an existing filename, seems to fix some problems with 'find by.Dir' sample
	renameOut = {name : "dexvert"};

	// If the output is exactly this big, then the conversion didn't produce anything
	verify = (r, dexFile) => dexFile.size!==263_100;

	// We send all macromediaDirector files through dirOpener first to decrypt any that are encrypted. If they are not encrypted, dirOpener outputs the same file, which is fine
	allowDupOut = true;

	chain = "macromediaDirector";
}

