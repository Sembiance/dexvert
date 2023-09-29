import {xu, fg} from "xu";
import {path} from "std";
import {RUNTIME} from "./Program.js";

export const OS_SERVER_HOST = "127.0.0.1";
export const OS_SERVER_PORT = 17735;
export const OSIDS = ["win2k", "winxp", "amiga"];

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
EndFunc`,
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
	AutoItSetOption("SendKeyDelay", $delay)
	Send($text)
	AutoItSetOption("SendKeyDelay", 5)
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

export async function run({f, cmd, osid="win2k", args=[], cwd, meta, script, scriptPre, timeout=xu.MINUTE*5, dontMaximize, quoteArgs, noAuxFiles, alsoKill=[], xlog})
{
	let fullCmd = cmd;
	const osData = {osid, cmd, meta, timeout, outDirPath : f.outDir.absolute};

	if(RUNTIME.globalFlags.osPriority)
		osData.osPriority = true;
	
	const inFiles = [f.input];
	if(!noAuxFiles)
		inFiles.push(...(f.files.aux || []));
	const inFilesRel = inFiles.map(v => v.rel);
	osData.inFilePaths = inFiles.map(v => v.absolute);

	const scriptLines = [];
	let binAndArgs = "";
	if(osid.startsWith("win"))
	{
		fullCmd = (/^[A-Za-z]:/).test(cmd) ? cmd : `c:\\dexvert\\${cmd}`;
		binAndArgs += `"${fullCmd}"`;

		const q = quoteArgs ? '"' : "";
		if(args.length>0)
			binAndArgs += ` ${args.map(v => (inFilesRel.includes(v) ? `c:\\in\\${path.basename(v)}` : v)).map(v => `${q}${v.split("").map(c => ([" ", "'"].includes(c) ? `' & "${c}" & '` : (c==='"' ? `' & '"' & '` : c))).join("")}${q}`).join(" ")}`;
	}
	else if(osid.startsWith("amiga"))
	{
		binAndArgs += cmd;
		if(args.length>0)
			binAndArgs += ` ${args.map(arg => (inFilesRel.includes(arg) ? (path.basename(arg).includes(" ") ? `"HD:in/${path.basename(arg)}"` : `HD:in/${path.basename(arg)}`) : (arg.includes(" ") && !arg.includes('"') ? `"${arg}"` : arg))).join(" ")}`;
	}

	if(osid.startsWith("win"))
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

					Sleep(50)
				Until TimerDiff($exitDismissTimer) > ${xu.SECOND}

				; This will move the mouse over the systray area, causing any 'aborted' program icons to be removed
				MouseMove(312, 756, 1)
				MouseMove(1000, 756, 15)
			EndFunc
		`);

		scriptLines.push(`$osProgramPID = Run${script ? "" : (timeout ? "WaitWithTimeout" : "Wait")}('${binAndArgs}', '${cwd || "c:\\in"}'${dontMaximize ? "" : ", @SW_MAXIMIZE"}${script || !timeout ? "" : `, ${timeout}`})`);
		if(script)
			scriptLines.push(script);
	}
	else if(osid.startsWith("amiga"))
	{
		// Build an Amiga script
		scriptLines.push("/* dexvert go script */");	// A comment on the first line is REQUIRED for a script to be runnable!
		if(script)
			scriptLines.push(...Array.force(script));
		else
			scriptLines.push(`ADDRESS command ${binAndArgs.includes(`"`) ? `'` : `"`}${binAndArgs}${binAndArgs.includes(`"`) ? `'` : `"`}`);
		
		scriptLines.push("EXIT");
	}

	osData.script = scriptLines.join("\n");

	xlog.info`Running OS ${fg.peach(osid)} ${fg.orange(cmd)} ${args.map(arg => (arg.includes(" ") ? `"${arg}"` : arg)).join(" ")}`;
	xlog.debug`osData: ${osData}`;
	xlog.debug`\tSCRIPT: ${osData.script}`;
	const r = await (await fetch(`http://${OS_SERVER_HOST}:${OS_SERVER_PORT}/osRun`, {method : "POST", headers : { "content-type" : "application/json" }, body : JSON.stringify(osData)})).text();
	if(r!=="ok")
		throw new Error(r);
		
	return r;
}
