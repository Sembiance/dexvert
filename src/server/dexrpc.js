import {xu} from "xu";
import {path} from "std";
import {init as initPrograms, programDirPath} from "../program/programs.js";
import {init as initFormats, formatDirPath} from "../format/formats.js";
import {fileUtil, webUtil, cmdUtil} from "xutil";
import {DEXRPC_HOST, DEXRPC_PORT, DEV_MACHINE} from "../dexUtil.js";
import {AgentPool} from "AgentPool";
import {XLog} from "xlog";

const argv = cmdUtil.cmdInit({
	cmdid   : "dexserver-dexrpc",
	version : "1.0.0",
	desc    : "Pre-starts a bunch of dexvert and dexid agents to be able to evenly distribute CPU load and handle crashes, etc",
	opts    :
	{
		startedFilePath : {desc : "Path to write a file to when the server has started", hasValue : true, required : true},
		stopFilePath    : {desc : "Path to watch for a file to be created to stop the server", hasValue : true, required : true},
		logLevel        : {desc : "What level to use for logging. Valid: none fatal error warn info debug trace. Default: info", defaultValue : "info"}
	}});

const xlog = new XLog(argv.logLevel);
const DEXVERT_AGENT_COUNT = Math.floor(navigator.hardwareConcurrency*0.75);
const DEXID_AGENT_COUNT = Math.floor(navigator.hardwareConcurrency*0.30);
const LOCKS = new Set();
const RPC_RESPONSES = new Map();
let RPCID_COUNTER = 1;

xlog.info`Starting dexrpc server...`;

// we do this once here, because we will be starting like 20+ workers at once and if we don't prime the deno cache here first, the workers get a lot of contention and it's super slow
xlog.info`Priming deno cache for programs and formats...`;
await initPrograms();
await initFormats();

const onSuccess = ({changeResult, err, r}, {log, msg}) =>
{
	if(changeResult)
		return console.log(changeResult);

	if(!msg?.rpcid)
		return xlog.error`rpcid not set for agent response: ${{msg, err, r, log}}`;

	RPC_RESPONSES.set(msg.rpcid, err ? {log, err} : {log, r});
};

const onFail = ({reason, error}, {log, msg}) =>
{
	xlog.error`agent failed: ${reason}: ${error} ${log} ${msg}`;
	RPC_RESPONSES.set(msg.rpcid, {err : `${reason}: ${error}`, log});
};

const dexPool = new AgentPool(path.join(import.meta.dirname, "dex.agent.js"), {onSuccess, onFail, xlog});
const idPool = new AgentPool(path.join(import.meta.dirname, "dex.agent.js"), {onSuccess, onFail, xlog});

await dexPool.init({maxProcessDuration : (xu.HOUR*2)+(xu.MINUTE*10)});
await idPool.init({maxProcessDuration : (xu.HOUR*2)+(xu.MINUTE*10)});

const runEnv = {};
for(const [key, value] of Object.entries(Deno.env.toObject()))
{
	if(key.startsWith("DEX_"))
		runEnv[key] = value;
}

xlog.info`Starting ${DEXVERT_AGENT_COUNT} dexvert agents...`;
await dexPool.start({qty : DEXVERT_AGENT_COUNT, runEnv});

xlog.info`Starting ${DEXID_AGENT_COUNT} dexid agents...`;
await idPool.start({qty : DEXID_AGENT_COUNT, runEnv});

const monitors = [];
if(DEV_MACHINE)
{
	xlog.info`Starting format & program monitors...`;
	const monitorsReady = [];
	const changeHandler = async (op, change) =>
	{
		if(change.type==="ready")
			return monitorsReady.push(op);

		await [idPool, dexPool].parallelMap(async pool => await pool.broadcast({op, change}));
	};

	monitors.push(await fileUtil.monitor(formatDirPath, async change => await changeHandler("formatChange", change)));
	monitors.push(await fileUtil.monitor(programDirPath, async change => await changeHandler("programChange", change)));
	await xu.waitUntil(() => monitorsReady.length===monitors.length);
}

xlog.info`Starting web RPC...`;

const routes = new Map();

routes.set("/agentCount", () => new Response(DEXVERT_AGENT_COUNT.toString()));
routes.set("/status", () => new Response(JSON.stringify({idPool : idPool.status({simpleLog : true}), dexPool : dexPool.status({simpleLog : true})})));

routes.set("/dex", async request =>
{
	const workerData = await request.json();
	workerData.rpcid = RPCID_COUNTER++;
	if(["trace", "debug"].includes(workerData.logLevel))
		workerData.liveOutput = true;
	if(RPCID_COUNTER>10_000_000)
		RPCID_COUNTER = 1;

	(workerData.op==="dexid" ? idPool : dexPool).process([workerData]);
	await xu.waitUntil(() => RPC_RESPONSES.has(workerData.rpcid));
	const response = RPC_RESPONSES.get(workerData.rpcid);
	RPC_RESPONSES.delete(workerData.rpcid);
	return new Response(JSON.stringify(response));
});

routes.set("/lock", async request =>
{
	const data = await request.json();
	if(!data?.lockid?.length || LOCKS.has(data.lockid))
		return new Response("false");
		
	LOCKS.add(data.lockid);
	return new Response("true");
});

routes.set("/unlock", async request =>
{
	const data = await request.json();
	if(!data?.lockid?.length || !LOCKS.has(data.lockid))
		return new Response("false");
		
	LOCKS.delete(data.lockid);
	return new Response("true");
});

const webServer = webUtil.serve({hostname : DEXRPC_HOST, port : DEXRPC_PORT}, await webUtil.route(routes), {xlog});
await fileUtil.writeTextFile(argv.startedFilePath, "");

// wait until we are told to stop
await xu.waitUntil(async () => await fileUtil.exists(argv.stopFilePath));
xlog.info`Stopping...`;
webServer.stop();
await monitors.parallelMap(async monitor => await monitor?.stop());
await [dexPool, idPool].parallelMap(async pool => await pool?.stop());

await fileUtil.unlink(argv.stopFilePath);
