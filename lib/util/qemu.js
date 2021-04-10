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

// AUTOIT DOCS: https://www.autoitscript.com/autoit3/docs/functions.htm
// Send() Keys: https://www.autoitscript.com/autoit3/docs/functions/Send.htm
exports.run = function run({cmd, osid="win2k", args=[], cwd, autoIt, inFilePaths=[], timeout=XU.MINUTE*5})
{
	return (state, p, cb) =>
	{
		tiptoe(
			function prepare()
			{
				const qemuData = {osid, timeout, outDirPath : state.output.absolute};
				if(inFilePaths.length>0)
					qemuData.inFilePaths = inFilePaths.map(inFilePath => (inFilePath.startsWith("/") ? inFilePath : path.resolve(state.cwd, inFilePath)));
				
				let binAndArgs = `"${(/^[A-Za-z]:/).test(cmd) ? cmd : `c:\\dexvert\\${cmd}`}"`;
				if(args.length>0)
					binAndArgs += ` ${args.map(arg => (inFilePaths.includes(arg) ? `"c:\\in\\${path.basename(arg)}"` : (arg.includes(" ") && !arg.includes('"') ? `"${arg}"` : arg))).join(" ")}`;

				const autoItParts = [];
				if(!autoIt && timeout)
					autoItParts.push(autoItFuncs.RunWaitWithTimeout);

				autoItParts.push(`Run${autoIt ? "" : (timeout ? "WaitWithTimeout" : "Wait")}('${binAndArgs}', '${cwd || "c:\\in"}', @SW_MAXIMIZE${autoIt || !timeout ? "" : `, ${timeout}`})`);
				if(autoIt)
					autoItParts.push(autoIt);
				
				qemuData.autoIt = autoItParts.join("\n");

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
