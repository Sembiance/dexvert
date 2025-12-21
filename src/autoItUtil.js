import {xu} from "xu";
import {path} from "std";

// AUTOIT FUNCTIONS: https://www.autoitscript.com/autoit3/docs/functions.htm
// AUTOIT LIB FUNCTIONS: https://www.autoitscript.com/autoit3/docs/libfunctions.htm
// Send() Keys: https://www.autoitscript.com/autoit3/docs/functions/Send.htm
// AUTOIT DLL INFO: https://www.autoitscript.com/forum/topic/93496-tutorial-on-dllcall-dllstructs/
const AUTOIT_FUNCS = {
	// TimerInit and TimerDiff are 100% NOT TRUSTWORTHY! They will report that 60,000ms has gone by when in reality only 3 or 4 seconds have gone by. AutoIt does warn that it doesn't work on some processors. So we roll our own here
	GetTime : `
#include <Date.au3>
Func GetTime()
	return _Date_Time_GetTickCount()
EndFunc
`,
	TimeDiff : `
Func TimeDiff($startTime)
	return _Date_Time_GetTickCount() - $startTime
EndFunc
`,
	KillAll : `
Func KillAll($program)
	Do
		Local $result = ProcessClose($program)
		If $result = 1 Then
			Sleep(500)
		EndIf
	Until $result Not = 1
EndFunc
`,
	DirCopyContents : `
Func DirCopyContents($dir, $targetDir)
	Local $search = FileFindFirstFile($dir & "\\*")
	If $search = -1 Then Return 0
	While 1
		Local $file = FileFindNextFile($search)
		If @error Then ExitLoop
		If $file = "." Or $file = ".." Then ContinueLoop
		Local $fullPath = $dir & "\\" & $file
		If StringInStr(FileGetAttrib($fullPath), "D") Then
			DirCopy($fullPath, $targetDir & "\\" & $file, 1)
		Else
			FileCopy($fullPath, $targetDir & "\\" & $file)
		EndIf
	WEnd
	FileClose($search)
EndFunc
`,
	DirFileCount : `
Func DirFileCount($dir)
	Local $total = 0, $search = FileFindFirstFile($dir & "\\*")
	If $search = -1 Then Return 0
	While 1
		Local $file = FileFindNextFile($search)
		If @error Then ExitLoop
		If $file = "." Or $file = ".." Then ContinueLoop
		Local $fullPath = $dir & "\\" & $file
		If StringInStr(FileGetAttrib($fullPath), "D") Then
			$total += DirFileCount($fullPath)
		Else
			$total += 1
		EndIf
	WEnd
	FileClose($search)
	Return $total
EndFunc	
`,
	DirEmpty : `
Func DirEmpty($dir)
	Local $search = FileFindFirstFile($dir & "\\*")
	If $search = -1 Then Return 0
	While 1
		Local $file = FileFindNextFile($search)
		If @error Then ExitLoop
		If $file = "." Or $file = ".." Then ContinueLoop
		Local $fullPath = $dir & "\\" & $file
		If StringInStr(FileGetAttrib($fullPath), "D") Then
			DirRemove($fullPath, 1)
		Else
			FileDelete($fullPath)
		EndIf
	WEnd
	FileClose($search)
EndFunc
`,
	ListCDirs : `
#include <Array.au3>
Func ListCDirs()
	Local $cSearch, $cDir, $cDirs[1]
	$cSearch = FileFindFirstFile("C:\\*.*")
	If $cSearch <> -1 Then
		While 1
			$cDir = FileFindNextFile($cSearch)
			If @error Then ExitLoop

			If StringInStr(FileGetAttrib("C:\\" & $cDir), "D") Then
				ReDim $cDirs[UBound($cDirs) + 1]
				$cDirs[UBound($cDirs) - 1] = $cDir
			EndIf
		WEnd
		FileClose($cSearch)
	EndIf
	_ArraySort($cDirs)

	return $cDirs
EndFunc
`,
	MouseClickWin : `
Func MouseClickWin($title, $button, $x, $y, $clicks=1)
	Local $winPos = WinGetPos($title)
	MsgBox(0, "debug", String($winPos[0]) & "x" & String($winPos[1]) & String($winPos[0]+$x))
	MouseClick($button, $winPos[0]+$x, $winPos[1]+$y, $clicks)
EndFunc
`,
	WaitForClipChange : `
Func WaitForClipChange($max_duration)
	Local $startValue = ClipGet()
	Local $clipChangeTimer = GetTime()
	Do
		If Not (ClipGet() == $startValue) Then ExitLoop
		Sleep(50)
	Until TimeDiff($clipChangeTimer) > $max_duration
EndFunc
`,
	WaitForControl : `
Func WaitForControl($title, $text, $controlID, $max_duration, $errorWindowTitle=0, $errowWindowButton=0, $errorWindowTitleEscape=0)
	Local $controlHandle
	Local $controlWaitTimer = GetTime()
	Do
		If $errorWindowTitle Then
			If WinActive($errorWindowTitle, "") Not = 0 Then ControlClick($errorWindowTitle, "", $errowWindowButton)
		EndIf

		If $errorWindowTitleEscape Then
			If WinActive($errorWindowTitleEscape, "") Not = 0 Then Send("{ESCAPE}")
		EndIf

		$controlHandle = ControlGetHandle($title, $text, $controlID)
		If $controlHandle Then ExitLoop
		Sleep(50)
	Until TimeDiff($controlWaitTimer) > $max_duration

	return $controlHandle
EndFunc
`,
	WaitForStableFileSize : `
Func WaitForStableFileSize($filePath, $stableDuration, $maxDuration)
	Local $lastSize = 0
	Local $stableSizeTimer = GetTime()
	Local $stableTimer = GetTime()
	Do
		Sleep(50)
		
		If Not FileExists($filePath) Then ContinueLoop

		$curSize = FileGetSize($filePath)
		If $curSize <> $lastSize Then
			$lastSize = $curSize
			$stableTimer = GetTime()
		ElseIf TimeDiff($stableTimer) > $stableDuration Then
			ExitLoop
		EndIf
	Until TimeDiff($stableSizeTimer) > $maxDuration
EndFunc
`,
	WaitForStableDirCount : `
Func WaitForStableDirCount($dirPath, $stableDuration, $maxDuration)
	Local $lastCount = 0
	Local $stableCountTimer = GetTime()
	Local $stableTimer = GetTime()
	Do
		Sleep(50)
		
		If Not FileExists($dirPath) Then ContinueLoop

		$curCount = DirFileCount($dirPath)
		If $curCount <> $lastCount Then
			$lastCount = $curCount
			$stableTimer = GetTime()
		ElseIf TimeDiff($stableTimer) > $stableDuration Then
			ExitLoop
		EndIf
	Until TimeDiff($stableCountTimer) > $maxDuration
EndFunc
`,
	WaitForPID : `
Func WaitForPID($pid, $max_duration)
	Local $pidWaitTimer = GetTime()
	Do
		If Not ProcessExists($pid) Then ExitLoop
		Sleep(50)
	Until TimeDiff($pidWaitTimer) > $max_duration

	return ProcessExists($pid)
EndFunc`,
	RunWaitWithTimeout : `
Func RunWaitWithTimeout($program, $workingdir, $show_flag, $max_duration)
	Local $pid = Run($program, $workingdir, $show_flag)
	WaitForPID($pid, $max_duration)
	If ProcessExists($pid) Then
		ProcessClose($pid)
	EndIf
EndFunc`,
	SaveClipboardWithMSPaint : `
Func SaveClipboardWithMSPaint($winDir, $outFilePath)
	Run('"C:\\' & $winDir & '\\SYSTEM32\\MSPAINT.EXE"', 'c:\\out', @SW_MAXIMIZE)

	$msPaintWindowVisible = WinWaitActive("[CLASS:MSPaintApp]", "", 10)
	If $msPaintWindowVisible Not = 0 Then
		Send("^v")

		$enlargeVisible = WinWaitActive("[CLASS:#32770]", "", 10)
		If $enlargeVisible Not = 0 Then
			ControlClick("[CLASS:#32770]", "", "[CLASS:Button; TEXT:&Yes]")
		EndIf

		ClipPut("")

		Sleep(250)

		Send("!f")
		Sleep(200)
		Send("a")

		WinWaitActive("[TITLE:Save As]", "", 10)

		Sleep(200)
		Send($outFilePath & "{TAB}p{ENTER}")

		WinWaitClose("[TITLE:Save As]", "", 10)
		Sleep(200)

		Send("!f")
		Sleep(200)
		Send("x")
		Sleep(200)
		Send("n")

		WinWaitClose("[CLASS:MSPaintApp]", "", 10)
	EndIf
EndFunc`,
	WindowRequire : `
Func WindowRequire($title, $text, $max_duration)
	Local $win = WinWaitActive($title, $text, $max_duration)
	If $win = 0 Then
		Exit 0
	EndIf

	return $win
EndFunc`,
	WindowFailure : `
Func WindowFailure($title, $text, $max_duration, $dismissKeys=0)
	Local $win = 0
	If $max_duration = -1 Then
		$win = WinActive($title, $text)
	Else
		$win = WinWaitActive($title, $text, $max_duration)
	EndIf

	If $win Not = 0 Then
		If $dismissKeys Not = 0 Then
			Send($dismissKeys)
		EndIf
		Exit 0
	EndIf
EndFunc`,
	WindowDismissWait : `
Func WindowDismissWait($title, $text, $max_duration, $dismissKeys=0, $dismissFunc=0)
	Local $win = WinWaitActive($title, $text, $max_duration)
	If $win Not = 0 Then
		If $dismissFunc Not = 0 Then
			Call($dismissFunc)
			WinWaitClose($win, $text, $max_duration)
		EndIf
		If $dismissKeys Not = 0 Then
			Send($dismissKeys)
			WinWaitClose($win, $text, $max_duration)
		EndIf
		return $win
	EndIf
	return 0
EndFunc`,
	WindowDismiss : `
Func WindowDismiss($title, $text, $dismissKeys=0, $dismissFunc=0)
	Local $win = WinActive($title, $text)
	If $win Not = 0 Then
		If $dismissFunc Not = 0 Then
			Call($dismissFunc)
			WinWaitClose($win, $text, 2)
		EndIf
		If $dismissKeys Not = 0 Then
			Send($dismissKeys)
			WinWaitClose($win, $text, 2)
		EndIf
		return $win
	EndIf
	return 0
EndFunc`,
	CallUntil : `
Func CallUntil($funcName, $max_duration)
	Local $done = 0
	Local $callUntilTimer = GetTime()
	Do
		$done = Call($funcName)

		If $done Not = 0 Then ExitLoop
		Sleep(25)
	Until TimeDiff($callUntilTimer) > $max_duration

	return $done
EndFunc`,
	SendSlow : `
Func SendSlow($text, $delay=200)
	$prevDelay = AutoItSetOption("SendKeyDelay", $delay)
	Send($text)
	AutoItSetOption("SendKeyDelay", $prevDelay)
EndFunc`,
	Pause : `
Func Pause($msg="pause")
	MsgBox(0, "pause", $msg)
EndFunc`,
	DebugListWindowTitles : `
	Func DebugListWindowTitles()
		Local $aList = WinList()

		; Loop through the array displaying only visible windows with a title.
		For $i = 1 To $aList[0][0]
			If $aList[$i][0] <> "" And BitAND(WinGetState($aList[$i][1]), 2) Then
				MsgBox(0, "", "Title: [" & $aList[$i][0] & "]" & @CRLF & "Handle: " & $aList[$i][1])
			EndIf
		Next
	EndFunc`
};
const AUTO_INCLUDE_FUNCS = ["GetTime", "TimeDiff", "KillAll"];
const FUNC_REQ_FUNCS = {
	WaitForStableDirCount : "DirFileCount"
};

export function appendCommonFuncs(scriptLines, {script, scriptPre, timeout, alsoKill=[], fullCmd, skipMouseMoving})
{
	const funcsToInclude = Array.from(AUTO_INCLUDE_FUNCS);
	if(!script && timeout)
		funcsToInclude.pushUnique("WaitForPID", "RunWaitWithTimeout");

	if(script)
		funcsToInclude.pushUnique(...Object.keys(AUTOIT_FUNCS).filter(funcName => script.includes(funcName)));
	if(scriptPre)
		funcsToInclude.pushUnique(...Object.keys(AUTOIT_FUNCS).filter(funcName => scriptPre.includes(funcName)));

	for(const [funcName, reqFuncs] of Object.entries(FUNC_REQ_FUNCS))
	{
		if(funcsToInclude.includes(funcName))
			funcsToInclude.pushUnique(...Array.force(reqFuncs));
	}

	scriptLines.push(...funcsToInclude.map(funcName => AUTOIT_FUNCS[funcName]).filter(v => !!v));

	if(scriptPre)
		scriptLines.push(scriptPre);

	scriptLines.push(`
		OnAutoItExitRegister("ExitHandler")
		Func ExitHandler()
			; Now kill our program
			KillAll("${path.basename(fullCmd.replaceAll("\\", "/"))}")
			KillAll("ntvdm.exe")
			${alsoKill.map(v => `KillAll("${v}")`).join("\n")}

			AutoItSetOption("WinTitleMatchMode", 2)

			; We can't do 'CallUntil()' or 'WindowDismiss()' here because we are within the Exit handler and can't call custom functions. sigh.
			Local $exitDismissTimer = GetTime()
			Do
				Local $exitErrorWin = WinActive("Program Error", "")
				If $exitErrorWin Not = 0 Then
					Send("{ENTER}")
				EndIf

				$exitErrorWin = WinActive("Application Error", "")
				If $exitErrorWin Not = 0 Then
					Send("{ENTER}")
				EndIf

				$exitErrorWin = WinActive("", "An error has occurred in your application")
				If $exitErrorWin Not = 0 Then
					ControlClick("", "An error has occurred in your application", "[CLASS:Button; TEXT:&Close]")
				EndIf

				$exitErrorWin = WinActive("", "has encountered a problem")
				If $exitErrorWin Not = 0 Then
					ControlClick("", "has encountered a problem", "[CLASS:Button; TEXT:&Don't Send]")
				EndIf

				$exitErrorWin = WinActive("Windows", "Check for solution")
				If $exitErrorWin Not = 0 Then
					ControlClick("Windows", "Check for solution", "[CLASS:Button; TEXT:Cancel]")
				EndIf

				Sleep(50)
			Until TimeDiff($exitDismissTimer) > ${xu.SECOND}

			; Just in case there is a random explorer window open (possibly with a random menu dropped down), I've seen it happen, close the menu then the window
			Send("{ESCAPE}{ESCAPE}^w")

			${!skipMouseMoving ? `; This will move the mouse over the systray area, causing any 'aborted' program icons to be removed
			MouseMove(312, 756, 1)
			MouseMove(1000, 756, 15)` : ""}
		EndFunc
	`);

	return scriptLines;
}
