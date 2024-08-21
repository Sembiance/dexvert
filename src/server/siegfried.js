import {xu} from "xu";
import {runUtil, cmdUtil, fileUtil} from "xutil";
import {XLog} from "xlog";

const argv = cmdUtil.cmdInit({
	cmdid   : "dexserver-siegfried",
	version : "1.0.0",
	desc    : "Runs and monitors the siegfried daemon which is used to help identify files",
	opts    :
	{
		startedFilePath : {desc : "Path to write a file to when the server has started", hasValue : true, required : true},
		stopFilePath    : {desc : "Path to watch for a file to be created to stop the server", hasValue : true, required : true},
		logLevel        : {desc : "What level to use for logging. Valid: none fatal error warn info debug trace. Default: info", defaultValue : "info"}
	}});

const xlog = new XLog(argv.logLevel);

let stopping = false;

let p = null;
let start = null;

const exitHandler = async ({success, code, signal}) =>
{
	if(stopping)
		return;

	xlog.error`Siegfried server exited unexpectedly (success: ${success}) with code: ${code}, signal: ${signal}`;
	await start();
};

start = async () =>
{
	xlog.info`Starting siegfried server...`;
	({p} = await runUtil.run("sf", ["-home", "/opt/siegfried-bin/siegfried/", "-nr", "-serve", "127.0.0.1:15138"], {detached : true, exitcb : async o => await exitHandler(o), stdoutcb : line => xlog.info`${line}`, stderrcb : line => xlog.warn`${line}`}));
};

await start();
await fileUtil.writeTextFile(argv.startedFilePath, "");

// wait until we are told to stop
await xu.waitUntil(async () => await fileUtil.exists(argv.stopFilePath));
xlog.info`Stopping...`;
stopping = true;
await runUtil.kill(p);
await fileUtil.unlink(argv.stopFilePath);
