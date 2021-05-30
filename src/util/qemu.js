"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	path = require("path"),
	C = require("../C.js"),
	httpUtil = require("@sembiance/xutil").http;

const autoItFuncs =
{
	RunWaitWithTimeout : `
Func RunWaitWithTimeout($program, $workingdir, $show_flag, $max_duration)
	$pid = Run($program, $workingdir, $show_flag)
	$timer = TimerInit()
	Do
		If Not ProcessExists($pid) Then ExitLoop
		Sleep(100)
	Until TimerDiff($timer) > $max_duration
	If ProcessExists($pid) Then
		ProcessClose($pid)
	EndIf
EndFunc`
};

// The hd.img files have a Startup supervisor.bat that will share c:\in and c:\out as network drives and will then run c:\dexvert\supervisor.au3 which will wait for c:\in\go.au3 and then execute it, wait for finish and then delete go.au3

// AUTOIT DOCS: https://www.autoitscript.com/autoit3/docs/functions.htm
// Send() Keys: https://www.autoitscript.com/autoit3/docs/functions/Send.htm
exports.run = function run({cmd, osid="win2k", args=[], cwd, script, inFilePaths=[], timeout=XU.MINUTE*5})
{
	return (state, p, cb) =>
	{
		tiptoe(
			function prepare()
			{
				const qemuData = {osid, timeout, outDirPath : state.output.absolute};
				if(inFilePaths.length>0)
					qemuData.inFilePaths = inFilePaths.map(inFilePath => (inFilePath.startsWith("/") ? inFilePath : path.resolve(state.cwd, inFilePath)));

				const scriptLines = [];
				let binAndArgs = "";
				if(osid.startsWith("win"))
				{
					const fullCMD = (/^[A-Za-z]:/).test(cmd) ? cmd : `c:\\dexvert\\${cmd}`;
					if(cmd.endsWith(".lnk"))
					{
						scriptLines.push(`$lnkInfo = FileGetShortcut("${fullCMD}")`);
						binAndArgs += `"' & $lnkInfo[0] & '"`;
					}
					else
					{
						binAndArgs += `"${fullCMD}"`;
					}

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

				if(osid.startsWith("win"))
				{
					// Build an AutoIt script
					if(!script && timeout)
						scriptLines.push(autoItFuncs.RunWaitWithTimeout);

					scriptLines.push(`Run${script ? "" : (timeout ? "WaitWithTimeout" : "Wait")}('${binAndArgs}', '${cwd || "c:\\in"}', @SW_MAXIMIZE${script || !timeout ? "" : `, ${timeout}`})`);
					if(script)
						scriptLines.push(script);
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
