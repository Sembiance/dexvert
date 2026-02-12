import {xu} from "xu";
import {cmdUtil, runUtil, fileUtil} from "xutil";
import {C} from "../C.js";
import {path} from "std";
import {XLog} from "xlog";

const argv = cmdUtil.cmdInit({
	cmdid   : "dexserver-classify",
	version : "1.0.0",
	desc    : "Handles checking output images to determine if they are 'garbage' or not",
	opts    :
	{
		startedFilePath : {desc : "Path to write a file to when the server has started", hasValue : true, required : true},
		stopFilePath    : {desc : "Path to watch for a file to be created to stop the server", hasValue : true, required : true},
		logLevel        : {desc : "What level to use for logging. Valid: none fatal error warn info debug trace. Default: info", defaultValue : "info"}
	}});

const xlog = new XLog(argv.logLevel);

xlog.info`Removing existing classify wip directories...`;
await fileUtil.unlink(C.CLASSIFY_PATH, {recursive : true}).catch(() => {});

xlog.info`Creating classify wip directories...`;
for(const name of ["__pycache__", "garbage", "tmp"])
	await Deno.mkdir(path.join(C.CLASSIFY_PATH, name), {recursive : true});

xlog.info`Starting classify server...`;
const classifyDirPath = path.join(import.meta.dirname, "..", "..", "classify");
const runOptions = {detached : true, cwd : classifyDirPath, env : {VIRTUAL_ENV : path.join(classifyDirPath, "env")}};
if(xlog.atLeast("debug"))
	runOptions.liveOutput = true;
const {p} = await runUtil.run(path.join(classifyDirPath, "env/bin/python3"), ["-X", `pycache_prefix=${path.join(C.CLASSIFY_PATH, "__pycache__")}`, "classifyServer.py"], runOptions);

xlog.info`Waiting for classify server to be available...`;
// wait for classify server to fully load
await xu.waitUntil(async () => (await (await fetch(`http://${C.CLASSIFY_HOST}:${C.CLASSIFY_PORT}/status`).catch(() => {}))?.json())?.status==="a-ok");
await fileUtil.writeTextFile(argv.startedFilePath, "");
xlog.info`Classify server started and ready!`;

// wait until we are told to stop
await xu.waitUntil(async () => await fileUtil.exists(argv.stopFilePath));
xlog.info`Stopping...`;
await runUtil.kill(p);
await fileUtil.unlink(argv.stopFilePath);
