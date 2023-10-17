import {xu} from "xu";
import {path} from "std";

// AUTOIT FUNCTIONS: https://www.autoitscript.com/autoit3/docs/functions.htm
// AUTOIT LIB FUNCTIONS: https://www.autoitscript.com/autoit3/docs/libfunctions.htm
// Send() Keys: https://www.autoitscript.com/autoit3/docs/functions/Send.htm
// AUTOIT DLL INFO: https://www.autoitscript.com/forum/topic/93496-tutorial-on-dllcall-dllstructs/
const AUTOIT_FUNCS =
{
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
	Local $timer = TimerInit()
	Do
		If Not (ClipGet() == $startValue) Then ExitLoop
		Sleep(50)
	Until TimerDiff($timer) > $max_duration
EndFunc
`,
	WaitForControl : `
Func WaitForControl($title, $text, $controlID, $max_duration, $errorWindowTitle=0, $errowWindowButton=0, $errorWindowTitleEscape=0)
	Local $controlHandle
	Local $timer = TimerInit()
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
	Until TimerDiff($timer) > $max_duration

	return $controlHandle
EndFunc
`,
	WaitForStableFileSize : `
Func WaitForStableFileSize($filePath, $stableDuration, $maxDuration)
	Local $lastSize = 0
	Local $timer = TimerInit()
	Local $stableTimer = TimerInit()
	Do
		Sleep(50)
		
		If Not FileExists($filePath) Then ContinueLoop

		$curSize = FileGetSize($filePath)
		If $curSize <> $lastSize Then
			$lastSize = $curSize
			$stableTimer = TimerInit()
		ElseIf TimerDiff($stableTimer) > $stableDuration Then
			ExitLoop
		EndIf
	Until TimerDiff($timer) > $maxDuration
EndFunc
`,
	WaitForPID : `
Func WaitForPID($pid, $max_duration)
	Local $timer = TimerInit()
	Do
		If Not ProcessExists($pid) Then ExitLoop
		Sleep(50)
	Until TimerDiff($timer) > $max_duration

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
	Local $timer = TimerInit()
	Do
		$done = Call($funcName)

		If $done Not = 0 Then ExitLoop
		Sleep(50)
	Until TimerDiff($timer) > $max_duration

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
				MsgBox(0, "", "Title: " & $aList[$i][0] & @CRLF & "Handle: " & $aList[$i][1])
			EndIf
		Next
	EndFunc`
};
const AUTO_INCLUDE_FUNCS = ["KillAll"];

export function appendCommonFuncs(scriptLines, {script, scriptPre, timeout, alsoKill=[], fullCmd, skipMouseMoving})
{
	// Build an AutoIt script
	scriptLines.push(...AUTO_INCLUDE_FUNCS.map(AUTO_INCLUDE_FUNC => AUTOIT_FUNCS[AUTO_INCLUDE_FUNC]));

	if(!script && timeout)
		scriptLines.push(AUTOIT_FUNCS.WaitForPID, AUTOIT_FUNCS.RunWaitWithTimeout);
	
	if(script)
		scriptLines.push(...Object.entries(AUTOIT_FUNCS).map(([funcName, funcText]) => (!AUTO_INCLUDE_FUNCS.includes(funcName) && script.includes(funcName) ? funcText : null)).filter(v => !!v));
	if(scriptPre)
	{
		scriptLines.push(...Object.entries(AUTOIT_FUNCS).map(([funcName, funcText]) => (!AUTO_INCLUDE_FUNCS.includes(funcName) && scriptPre.includes(funcName) ? funcText : null)).filter(v => !!v));
		scriptLines.push(scriptPre);
	}

	scriptLines.push(`
		OnAutoItExitRegister("ExitHandler")
		Func ExitHandler()
			; Now kill our program
			KillAll("${path.basename(fullCmd.replaceAll("\\", "/"))}")
			${alsoKill.map(v => `KillAll("${v}")`).join("\n")}

			AutoItSetOption("WinTitleMatchMode", 2)

			; We can't do 'CallUntil()' or 'WindowDismiss()' here because we are within the Exit handler and can't call custom functions. sigh.
			Local $exitDismissTimer = TimerInit()
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

				Sleep(50)
			Until TimerDiff($exitDismissTimer) > ${xu.SECOND}

			${!skipMouseMoving ? `; This will move the mouse over the systray area, causing any 'aborted' program icons to be removed
			MouseMove(312, 756, 1)
			MouseMove(1000, 756, 15)` : ""}
		EndFunc
	`);

	return scriptLines;
}
