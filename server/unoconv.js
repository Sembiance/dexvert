"use strict";
const XU = require("@sembiance/xu"),
	C = require("../lib/C.js"),
	runUtil = require("@sembiance/xutil").run;

let unoconvCP = null;
let stopping = false;

function startUnoconvServer()
{
	if(unoconvCP!==null)
		return;

	XU.log`Starting up unoconv server on port ${C.UNOCONV_PORT}`;

	unoconvCP = runUtil.run("unoconv", ["-p", C.UNOCONV_PORT, "-l"], {silent : true, detached : true});
	unoconvCP.on("exit", () =>
	{
		if(stopping)
			return;

		unoconvCP = null;

		XU.log`Unoconv server has exited, restarting...`;
		startUnoconvServer();
	});
}

// Starts up our unoconv background server
exports.start = function start(cb)
{
	startUnoconvServer();
	setImmediate(cb);
};

// Return true if everything is ok
exports.status = function status()
{
	return unoconvCP!==null;
};

// Stops our unoconv background server
exports.stop = function stop(cb)
{
	stopping = true;

	if(unoconvCP && !unoconvCP.killed)
	{
		unoconvCP.on("exit", () => setImmediate(cb));
		unoconvCP.kill();
	}
	else
	{
		setImmediate(cb);
	}
};
