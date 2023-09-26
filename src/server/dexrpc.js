import {xu} from "xu";
import {Server} from "../Server.js";
import {path} from "std";
import {WebServer} from "WebServer";
import {XWorkerPool} from "XWorkerPool";

// TODO some way to modify all 3 of these when running dexserver
export const DEXRPC_HOST = "127.0.0.1";
export const DEXRPC_PORT = 17750;
const DEX_WORKER_COUNT = 4;

export class dexrpc extends Server
{
	async start()
	{
		this.xlog.info`Starting dexrpc server...`;

		this.xlog.info`Starting ${DEX_WORKER_COUNT} workers...`;
		this.pool = new XWorkerPool({workercb : this.workercb.bind(this), xlog : this.xlog, crashRecover : true});

		await this.pool.start(path.join(xu.dirname(import.meta), "dexWorker.js"), {size : DEX_WORKER_COUNT});
		this.xlog.info`${DEX_WORKER_COUNT} workers ready!`;

		this.xlog.info`Starting web RPC...`;

		this.rpcData = {};
		this.rpcid = 0;

		this.webServer = new WebServer(DEXRPC_HOST, DEXRPC_PORT, {xlog : this.xlog});
		
		this.webServer.add("/dex", async (request, reply) =>
		{
			const workerData = await request.json();
			workerData.rpcid = this.rpcid++;
			this.rpcData[workerData.rpcid] = {reply, workerData};
			this.pool.process([workerData]);
		}, {detached : true, method : "POST", logCheck : () => false});

		await this.webServer.start();

		this.running = true;
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
			
		await this.pool?.stop();

		this.running = false;
	}
}
