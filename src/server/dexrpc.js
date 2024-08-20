import {xu} from "xu";
import {Server} from "../Server.js";
import {path} from "std";
import {XWorkerPool} from "XWorkerPool";
import {init as initPrograms, programDirPath} from "../program/programs.js";
import {init as initFormats, formatDirPath} from "../format/formats.js";
import {fileUtil, webUtil} from "xutil";

export const DEXRPC_HOST = "127.0.0.1";
export const DEXRPC_PORT = 17750;
const DEX_WORKER_COUNT = Math.floor(navigator.hardwareConcurrency*0.65);
const DEX_WORKER_ID_COUNT = Math.floor(navigator.hardwareConcurrency*0.20);
const LOCKS = new Set();

export class dexrpc extends Server
{
	async start()
	{
		this.xlog.info`Starting dexrpc server...`;

		// we do this once here, because we will be starting like 20+ workers at once and if we don't prime the deno cache here first, the workers get a lot of contention and it's super slow
		this.xlog.info`Priming deno cache for programs and formats...`;
		await initPrograms();
		await initFormats();

		this.xlog.info`Starting ${DEX_WORKER_COUNT} workers...`;
		this.dexPool = new XWorkerPool({workercb : this.workercb.bind(this), xlog : this.xlog, crashRecover : true});
		this.idPool = new XWorkerPool({workercb : this.workercb.bind(this), xlog : this.xlog, crashRecover : true});

		const runEnv = {};
		for(const [key, value] of Object.entries(Deno.env.toObject()))
		{
			if(key.startsWith("DEX_"))
				runEnv[key] = value;
		}

		await Promise.all([
			this.dexPool.start(path.join(import.meta.dirname, "dexWorker.js"), {size : DEX_WORKER_COUNT, runEnv}),
			this.idPool.start(path.join(import.meta.dirname, "dexWorker.js"), {size : DEX_WORKER_ID_COUNT, runEnv})]);

		this.xlog.info`${DEX_WORKER_COUNT} dex workers and ${DEX_WORKER_ID_COUNT} id workers ready!`;

		this.xlog.info`Starting format & program monitors...`;
		const monitorsReady = [];
		const changeHandler = async (op, change) =>
		{
			if(change.type==="ready")
				return monitorsReady.push(op);

			await [this.idPool, this.dexPool].parallelMap(async pool => await pool.broadcast({op, change}));
		};
		
		this.monitors = [
			await fileUtil.monitor(formatDirPath, async change => await changeHandler("formatChange", change)),
			await fileUtil.monitor(programDirPath, async change => await changeHandler("programChange", change))];
		
		await xu.waitUntil(() => monitorsReady.length===this.monitors.length);

		this.xlog.info`Starting web RPC...`;

		this.rpcData = {};
		this.rpcid = 0;

		const routes = new Map();

		routes.set("/workerCount", () => new Response(DEX_WORKER_COUNT.toString()));
		
		routes.set("/dex", async request =>
		{
			const workerData = await request.json();
			workerData.rpcid = this.rpcid++;

			let response = null;
			this.rpcData[workerData.rpcid] = {reply : v => { response = v; }, workerData};
			this[workerData.op==="dexid" ? "idPool" : "dexPool"].process([workerData]);
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

		this.webServer = webUtil.serve({hostname : DEXRPC_HOST, port : DEXRPC_PORT}, await webUtil.route(routes), {xlog : this.xlog});

		this.running = true;
	}

	async crashcb(workerid, status, r, logLines)
	{
		await this.workercb(workerid, {err : `worker ${workerid} crashed with status code ${status?.code} and logLines: ${logLines.join("\n")}`, ...r});
	}

	async workercb(workerid, {rpcid, logLines, err, r}={})	// eslint-disable-line require-await
	{
		const rpcData = this.rpcData[rpcid];

		if(err)
			this.xlog.error`worker ${workerid}: error: ${err} for rpcid ${rpcid}`;

		if(!rpcData?.reply)
			return this.xlog.error`worker ${workerid}: no rpcData.reply for rpcid ${rpcid} and r ${r} and logLines ${logLines}`;

		rpcData.reply(new Response(err ? `Error: ${err}` : JSON.stringify({logLines, r}), {status : err ? 500 : 200}));
	}

	async status()	// eslint-disable-line require-await
	{
		return this.running;
	}

	async stop()
	{
		if(this.webServer)
			this.webServer.stop();

		await this.monitors.parallelMap(async monitor => await monitor?.stop());
		await [this.dexPool, this.idPool].parallelMap(async pool => await pool?.stop());

		this.running = false;
	}
}
