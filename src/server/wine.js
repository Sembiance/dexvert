/* eslint-disable require-await */
import {xu, fg} from "xu";
import {Server} from "../Server.js";
import {runUtil, fileUtil} from "xutil";
import {path, delay} from "std";
import {WINE_PREFIX_SRC, WINE_PREFIX, WINE_WEB_HOST, WINE_WEB_PORT} from "../wineUtil.js";
import {WebServer} from "WebServer";

export class wine extends Server
{
	wineserverProcs = [];
	wineBaseEnv = {};
	WINE_BASES = [];
	wineCounter = 0;

	baseKeys = Object.keys(this);

	async start()
	{
		this.xlog.info`Cleaning up previous wine procs...`;
		for(const v of ["winedevice.exe", "services.exe", "explorer.exe", "plugplay.exe", "svchost.exe", "rpcss.exe"])
			await runUtil.run("killall", ["-9", v]);

		this.xlog.info`Preparing prefix bases...`;
		await fileUtil.unlink(WINE_PREFIX, {recursive : true});
		await Deno.mkdir(WINE_PREFIX, {recursive : true});

		const winePrefixDirPaths = await fileUtil.tree(WINE_PREFIX_SRC, {nofile : true, depth : 1});
		for(const winePrefixDirPath of winePrefixDirPaths)
		{
			const wineBase = path.basename(winePrefixDirPath);
			this.WINE_BASES.push(wineBase);

			await runUtil.run("rsync", runUtil.rsyncArgs(path.join(winePrefixDirPath, "/"), path.join(WINE_PREFIX, wineBase, "/"), {fast : true}));
		}

		this.xlog.info`Starting wineservers...`;
		for(const wineBase of this.WINE_BASES)
		{
			const runOpts = {detached : true, stdoutcb : line => this.xlog.info`${xu.colon(fg.orange(wineBase))}${line}`, stderrcb : line => this.xlog.warn`${xu.colon(fg.orange(wineBase))}${line}`};
			runOpts.env = {WINEPREFIX : path.join(WINE_PREFIX, wineBase)};
			if(this.xlog.atLeast("trace"))
			{
				runOpts.env.DISPLAY = ":0";
			}
			else
			{
				runOpts.virtualX = true;
				runOpts.virtualXVNCPort = true;
			}

			const {p, xvfbPort, virtualXVNCPort} = await runUtil.run("wineserver", ["--foreground", "--persistent"], runOpts);
			this.wineserverProcs.push(p);

			this.wineBaseEnv[wineBase] = {DISPLAY : (this.xlog.atLeast("trace") ? ":0" : `:${xvfbPort}`), WINEPREFIX : runOpts.env.WINEPREFIX};

			this.xlog.info`Wineserver ${fg.orange(wineBase)} started${runOpts.virtualXVNCPort ? ` (VNC Port: ${virtualXVNCPort})` : ""}`;
		}

		// Despite looking at the source code for wineserver, I couldn't find a definitive good way to determine that wineserver is 'fully loaded' and ready to go, so just sleep
		await delay(xu.SECOND*3);

		this.xlog.info`Running wineboots...`;
		for(const wineBase of this.WINE_BASES)
		{
			this.xlog.debug`Running wineboot for ${wineBase}...`;
			await runUtil.run("wineboot", ["--update"], {stdoutNull : true, stderrNull : true, env : this.wineBaseEnv[wineBase]});
		}

		this.xlog.info`Starting wine web server...`;
		this.webServer = new WebServer(WINE_WEB_HOST, WINE_WEB_PORT, {xlog : this.xlog});
		this.webServer.add("/getBaseEnv", async () => new Response(JSON.stringify(this.wineBaseEnv)), {logCheck : () => false});
		this.webServer.add("/getWineCounter", async () =>
		{
			const wineCounterNum = `${this.wineCounter++}`;
			if(this.wineCounter>9000)
				this.wineCounter = 0;
			return new Response(wineCounterNum);
		}, {logCheck : () => false});
		await this.webServer.start();

		this.xlog.debug`wineBaseEnv: ${this.wineBaseEnv}`;
		this.xlog.info`Wine started`;

		this.started = true;
	}

	async status()
	{
		return this.wineserverProcs.length===this.WINE_BASES.length && this.started;
	}

	async stop()
	{
		if(this.webServer)
			this.webServer.stop();

		for(const wineBase of this.WINE_BASES)
			await runUtil.run("wineboot", ["--end-session", "--shutdown", "--kill", "--force"], {env : this.wineBaseEnv[wineBase]});

		for(const p of this.wineserverProcs)
			await runUtil.kill(p);

		this.xlog.debug`Deleting wine prefix bases...`;
		await fileUtil.unlink(WINE_PREFIX, {recursive : true});

		this.started = false;
	}
}
