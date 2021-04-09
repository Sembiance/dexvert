"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	path = require("path"),
	C = require("../C.js"),
	httpUtil = require("@sembiance/xutil").http;

// AUTOIT DOCS: https://www.autoitscript.com/autoit3/docs/functions.htm
// Send() Keys: https://www.autoitscript.com/autoit3/docs/functions/Send.htm

// Returns a function that when called will run wine with the given cmd and args and optional autoItScript
exports.run = function run({cmd, osid="win2k", args=[], cwd, autoIt, inFilePaths=[], timeout=XU.MINUTE*10})
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

				qemuData.autoIt = `Run${autoIt ? "" : "Wait"}('${binAndArgs}', '${cwd || "c:\\in"}', @SW_MAXIMIZE)`;
				if(autoIt)
					qemuData.autoIt += `\n${autoIt}`;

				XU.log`qemu.run with ${qemuData}`;
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
