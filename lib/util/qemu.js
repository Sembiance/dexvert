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
				
				// If we don't have an autoIt script, we are just a basic program execution with args. Try and auto-magic figure out the proper au3 script to execute the program
				if(!autoIt)
				{
					let binAndArgs = `"${(/^[A-Za-z]:/).test(cmd) ? cmd : `c:\\dexvert\\${cmd}`}"`;
					if(args.length>0)
						binAndArgs += ` ${args.map(arg => (inFilePaths.includes(arg) ? `"c:\\in\\${path.basename(arg)}"` : `"${arg}"`)).join(" ")}`;

					qemuData.autoIt = `RunWait('${binAndArgs}', '${cwd || ""}', @SW_MAXIMIZE)`;
				}

				XU.log`qemu.run with ${qemuData}`;
				httpUtil.post(`http://${C.DEXSERV_HOST}:${C.DEXSERV_PORT}/qemuRun`, qemuData, {postAsJSON : true}, this);
			},
			function debugOutput(...a)
			{
				XU.log`${a}`;
				this();
			},
			cb
		);
	};
};
