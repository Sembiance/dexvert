import {xu, fg} from "xu";
import {path} from "std";

export const QEMU_SERVER_HOST = "127.0.0.1";
export const QEMU_SERVER_PORT = 17735;
export const QEMUIDS = ["win2k", "winxp", "amigappc", "gentoo"];

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
EndFunc`,
	RunWaitWithTimeout : `
Func RunWaitWithTimeout($program, $workingdir, $show_flag, $max_duration)
	Local $pid = Run($program, $workingdir, $show_flag)
	WaitForPID($pid, $max_duration)
	If ProcessExists($pid) Then
		ProcessClose($pid)
	EndIf
EndFunc`
};

export async function run({f, cmd, osid="win2k", args=[], cwd, script, timeout=xu.MINUTE*5, dontMaximize, xlog})
{
	let fullCmd = cmd;
	const qemuData = {osid, timeout, outDirPath : f.outDir.absolute};
	
	const inFiles = [f.input, ...(f.files.aux || [])];
	const inFilesRel = inFiles.map(v => v.rel);
	qemuData.inFilePaths = inFiles.map(v => v.absolute);

	const scriptLines = [];
	let binAndArgs = "";
	if(osid.startsWith("win"))
	{
		fullCmd = (/^[A-Za-z]:/).test(cmd) ? cmd : `c:\\dexvert\\${cmd}`;
		binAndArgs += `"${fullCmd}"`;

		if(args.length>0)
		{
			binAndArgs += ` ${args.map(v => (inFilesRel.includes(v) ? `c:\\in\\${path.basename(v)}` : v)).map(_v =>
			{
				let v = _v;
				[" ", "'"].forEach(c => { v = v.replaceAll(c, `' & "${c}" & '`); });
				return v;
			}).join(" ")}`;
		}
	}
	else if(osid.startsWith("amiga"))
	{
		binAndArgs += cmd;
		if(args.length>0)
			binAndArgs += ` ${args.map(arg => (inFilesRel.includes(arg) ? (path.basename(arg).includes(" ") ? `"HD:in/${path.basename(arg)}"` : `HD:in/${path.basename(arg)}`) : (arg.includes(" ") && !arg.includes('"') ? `"${arg}"` : arg))).join(" ")}`;
	}
	else if(osid.startsWith("gentoo"))
	{
		binAndArgs += `${cmd} ${args.map(v => (inFilesRel.includes(v) ? path.basename(v) : v)).map(v => `'${v.replaceAll("'", `'"'"'`)}'`).join(" ")}`;
	}

	if(osid.startsWith("win"))
	{
		// Build an AutoIt script
		scriptLines.push(AUTOIT_FUNCS.KillAll);

		if(!script && timeout)
			scriptLines.push(AUTOIT_FUNCS.WaitForPID, AUTOIT_FUNCS.RunWaitWithTimeout);
		else
			scriptLines.push(...Object.entries(AUTOIT_FUNCS).map(([funcName, funcText]) => (script.includes(funcName) ? funcText : null)).filter(v => !!v));

		scriptLines.push(`Run${script ? "" : (timeout ? "WaitWithTimeout" : "Wait")}('${binAndArgs}', '${cwd || "c:\\in"}'${dontMaximize ? "" : ", @SW_MAXIMIZE"}${script || !timeout ? "" : `, ${timeout}`})`);
		if(script)
			scriptLines.push(script);
		
		scriptLines.push(`KillAll("${path.basename(fullCmd.replaceAll("\\", "/"))}")`);
	}
	else if(osid.startsWith("amiga"))
	{
		// Build an Amiga script
		scriptLines.push("/* dexvert go script */");
		scriptLines.push(`ADDRESS command "${binAndArgs}"`);

		if(script)
			scriptLines.push(script);
		
		scriptLines.push("EXIT");
	}
	else if(osid.startsWith("gentoo"))
	{
		scriptLines.push(`#!/bin/bash`);
		scriptLines.push(`${timeout ? `timeout ${Math.floor(timeout/xu.SECOND)}s ` : ""}${binAndArgs}`);
		scriptLines.push("sync");

		if(script)
			scriptLines.push(script);
	}

	qemuData.script = scriptLines.join("\n");

	xlog.info`Running QEMU ${fg.peach(osid)} ${fg.orange(cmd)} ${args.map(arg => (arg.includes(" ") ? `"${arg}"` : arg)).join(" ")}`;
	xlog.trace`\tSCRIPT: ${qemuData.script}`;
	const r = await (await fetch(`http://${QEMU_SERVER_HOST}:${QEMU_SERVER_PORT}/qemuRun`, {method : "POST", headers : { "content-type" : "application/json" }, body : JSON.stringify(qemuData)})).text();
	if(r!=="ok")
		throw new Error(r);
		
	return r;
}
