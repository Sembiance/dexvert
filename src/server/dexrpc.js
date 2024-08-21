import {xu} from "xu";
import {path} from "std";
import {XWorkerPool} from "XWorkerPool";
import {init as initPrograms, programDirPath} from "../program/programs.js";
import {init as initFormats, formatDirPath} from "../format/formats.js";
import {fileUtil, webUtil, cmdUtil} from "xutil";
import {DEXRPC_HOST, DEXRPC_PORT} from "../dexUtil.js";
import {XLog} from "xlog";

const argv = cmdUtil.cmdInit({
	cmdid   : "dexserver-dexrpcz",
	version : "1.0.0",
	desc    : "Pre-starts a bunch of dexvert and dexid agents to be able to evenly distribute CPU load and handle crashes, etc",
	opts    :
	{
		startedFilePath : {desc : "Path to write a file to when the server has started", hasValue : true, required : true},
		stopFilePath    : {desc : "Path to watch for a file to be created to stop the server", hasValue : true, required : true},
		logLevel        : {desc : "What level to use for logging. Valid: none fatal error warn info debug trace. Default: info", defaultValue : "info"}
	}});

const xlog = new XLog(argv.logLevel);
const DEX_WORKER_COUNT = Math.floor(navigator.hardwareConcurrency*0.65);
const DEX_WORKER_ID_COUNT = Math.floor(navigator.hardwareConcurrency*0.20);
const LOCKS = new Set();
const RPC_DATA = {};
let RPCID_COUNTER = 0;

xlog.info`Starting dexrpc server...`;

// we do this once here, because we will be starting like 20+ workers at once and if we don't prime the deno cache here first, the workers get a lot of contention and it's super slow
xlog.info`Priming deno cache for programs and formats...`;
await initPrograms();
await initFormats();

const workercb = async (workerid, {rpcid, logLines, err, r}={}) =>	// eslint-disable-line require-await
{
	const rpcData = RPC_DATA[rpcid];

	if(err)
		xlog.error`worker ${workerid}: error: ${err} for rpcid ${rpcid}`;

	if(!rpcData?.reply)
		return xlog.error`worker ${workerid}: no rpcData.reply for rpcid ${rpcid} and r ${r} and logLines ${logLines}`;

	rpcData.reply(new Response(err ? `Error: ${err}` : JSON.stringify({logLines, r}), {status : err ? 500 : 200}));
};

/*const crashcb = async (workerid, status, r, logLines) =>
{
	await workercb(workerid, {err : `worker ${workerid} crashed with status code ${status?.code} and logLines: ${logLines.join("\n")}`, ...r});
};*/

xlog.info`Starting ${DEX_WORKER_COUNT} workers...`;
const dexPool = new XWorkerPool({workercb, xlog, crashRecover : true});
const idPool = new XWorkerPool({workercb, xlog, crashRecover : true});

const runEnv = {};
for(const [key, value] of Object.entries(Deno.env.toObject()))
{
	if(key.startsWith("DEX_"))
		runEnv[key] = value;
}

await Promise.all([
	dexPool.start(path.join(import.meta.dirname, "dexWorker.js"), {size : DEX_WORKER_COUNT, runEnv}),
	idPool.start(path.join(import.meta.dirname, "dexWorker.js"), {size : DEX_WORKER_ID_COUNT, runEnv})]);

xlog.info`${DEX_WORKER_COUNT} dex workers and ${DEX_WORKER_ID_COUNT} id workers ready!`;

xlog.info`Starting format & program monitors...`;
const monitorsReady = [];
const changeHandler = async (op, change) =>
{
	if(change.type==="ready")
		return monitorsReady.push(op);

	await [idPool, dexPool].parallelMap(async pool => await pool.broadcast({op, change}));
};

const monitors = [
	await fileUtil.monitor(formatDirPath, async change => await changeHandler("formatChange", change)),
	await fileUtil.monitor(programDirPath, async change => await changeHandler("programChange", change))];

await xu.waitUntil(() => monitorsReady.length===monitors.length);

xlog.info`Starting web RPC...`;

const routes = new Map();

routes.set("/workerCount", () => new Response(DEX_WORKER_COUNT.toString()));

routes.set("/dex", async request =>
{
	const workerData = await request.json();
	workerData.rpcid = RPCID_COUNTER++;

	let response = null;
	RPC_DATA[workerData.rpcid] = {reply : v => { response = v; }, workerData};
	(workerData.op==="dexid" ? idPool : dexPool).process([workerData]);
	await xu.waitUntil(() => !!response);
	return response;
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
