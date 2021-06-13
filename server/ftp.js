"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs"),
	path = require("path"),
	tiptoe = require("tiptoe"),
	runUtil = require("@sembiance/xutil").run;

const FTP_BASE_DIR_PATH = "/mnt/ram/dexvert/ftp";
let vsftpdCP = null;
let stopping = false;

function startVSFTPD()
{
	if(vsftpdCP!==null)
		return;

	XU.log`VSFTPD server starting up...`;

	vsftpdCP = runUtil.run("vsftpd", [path.join(__dirname, "..", "ftp", "amigappc-vsftpd.conf")], {silent : true, detached : true});
	vsftpdCP.on("exit", () =>
	{
		if(stopping)
			return;

		vsftpdCP = null;

		XU.log`VSFTPD server has stopped! Restarting...`;
		startVSFTPD();
	});
}

// Starts up our FTP server
exports.start = function start(cb)
{
	tiptoe(
		function prepareFTPDirs()
		{
			["in", "out", "backup"].serialForEach((v, subcb) => fs.mkdir(path.join(FTP_BASE_DIR_PATH, v), {recursive : true}, subcb), this);
		},
		function startServer()
		{
			startVSFTPD();
			setImmediate(this);
		},
		cb
	);
};

// Return true if everything is ok
exports.status = function status()
{
	return startVSFTPD!==null;
};

// Stops our FTP server
exports.stop = function stop(cb)
{
	XU.log`VSFTPD stopping...`;
	
	stopping = true;

	if(vsftpdCP && !vsftpdCP.killed)
	{
		vsftpdCP.on("exit", () => setImmediate(cb));
		vsftpdCP.kill();
	}
	else
	{
		setImmediate(cb);
	}
};
