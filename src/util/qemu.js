"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	path = require("path"),
	C = require("../C.js"),
	httpUtil = require("@sembiance/xutil").http;

const autoItFuncs =
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

// The hd.img files have a Startup supervisor.bat that will share c:\in and c:\out as network drives and will then run c:\dexvert\supervisor.au3 which will wait for c:\in\go.au3 and then execute it, wait for finish and then delete go.au3

// AUTOIT DOCS: https://www.autoitscript.com/autoit3/docs/functions.htm
// Send() Keys: https://www.autoitscript.com/autoit3/docs/functions/Send.htm
exports.run = function run({cmd, osid="win2k", args=[], cwd, script, inFilePaths=[], timeout=XU.MINUTE*5, dontMaximize, outDirPath})
{
	let fullCmd = cmd;

	return (state, p, cb) =>
	{
		tiptoe(
			function prepare()
			{
				const qemuData = {osid, timeout, outDirPath : outDirPath || state.output.absolute};

				if(inFilePaths.length>0)
					qemuData.inFilePaths = inFilePaths.map(inFilePath => (inFilePath.startsWith("/") ? inFilePath : path.resolve(state.cwd, inFilePath)));

				const scriptLines = [];
				let binAndArgs = "";
				if(osid.startsWith("win"))
				{
					fullCmd = (/^[A-Za-z]:/).test(cmd) ? cmd : `c:\\dexvert\\${cmd}`;
					binAndArgs += `"${fullCmd}"`;

					if(args.length>0)
					{
						binAndArgs += ` ${args.map(v => (inFilePaths.includes(v) ? `c:\\in\\${path.basename(v)}` : v)).map(_v =>
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
						binAndArgs += ` ${args.map(arg => (inFilePaths.includes(arg) ? path.basename(arg).includes(" ") ? `"HD:in/${path.basename(arg)}"` : `HD:in/${path.basename(arg)}` : (arg.includes(" ") && !arg.includes('"') ? `"${arg}"` : arg))).join(" ")}`;
				}
				else if(osid.startsWith("gentoo"))
				{
					inFilePaths.forEach(inFilePath =>
					{
						if(inFilePath.startsWith("/"))
							args.replaceAll(inFilePath, path.basename(inFilePath));
					});

					binAndArgs += `${cmd} ${args.map(v => `'${v.replaceAll("'", `'"'"'`)}'`).join(" ")}`;
				}

				if(osid.startsWith("win"))
				{
					// Build an AutoIt script
					scriptLines.push(autoItFuncs.KillAll);

					if(!script && timeout)
						scriptLines.push(autoItFuncs.WaitForPID, autoItFuncs.RunWaitWithTimeout);
					else
						scriptLines.push(...Object.entries(autoItFuncs).map(([funcName, funcText]) => (script.includes(funcName) ? funcText : null)).filterEmpty());

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
					scriptLines.push(`${timeout ? `timeout ${Math.floor(timeout/XU.SECOND)}s ` : ""}${binAndArgs}`);
					scriptLines.push("sync");

					if(script)
						scriptLines.push(script);
				}

				qemuData.script = scriptLines.join("\n");

				if(state.verbose>=4)
					XU.log`Running QEMU: ${qemuData}`;

				httpUtil.post(`http://${C.DEXSERV_HOST}:${C.DEXSERV_PORT}/qemuRun`, qemuData, {postAsJSON : true}, this);
			},
			function debugOutput(a)
			{
				if(a.toString()!=="ok")
					throw new Error(a.toString());

				this();
			},
			cb
		);
	};
};
