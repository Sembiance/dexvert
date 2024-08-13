/* eslint-disable require-await */
import {xu, fg} from "xu";
import {Server} from "../Server.js";
import {runUtil, fileUtil, webUtil} from "xutil";
import {path, delay} from "std";
import {WINE_PREFIX_SRC, WINE_PREFIX, WINE_WEB_HOST, WINE_WEB_PORT} from "../wineUtil.js";

export class wine extends Server
{
	wineserverProcs = [];
	wineBaseEnv = {};
	WINE_BASES = [];
	wineCounter = 0;

	baseKeys = Object.keys(this);

	async start()
	{
		await this.cleanupProcs();

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
			if(this.xlog.atLeast("debug"))
			{
				runOpts.env.DISPLAY = ":0";
			}
			else
			{
				runOpts.virtualXGLX = true;	// Required for DirectorCastRipper to work (vs just virtualX)
				runOpts.virtualXVNCPort = true;
			}

			const {p, xvfbPort, virtualXVNCPort} = await runUtil.run("wineserver", ["--foreground", "--persistent"], runOpts);
			this.wineserverProcs.push(p);

			this.wineBaseEnv[wineBase] = {DISPLAY : (runOpts.env.DISPLAY || `:${xvfbPort}`), WINEPREFIX : runOpts.env.WINEPREFIX};

			this.xlog.info`Wineserver ${fg.orange(wineBase)} started (DISPLAY : ${this.wineBaseEnv[wineBase].DISPLAY})${runOpts.virtualXVNCPort ? ` (VNC ${virtualXVNCPort})` : ""}`;
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
		
		const routes = new Map();
		routes.set("/getBaseEnv", async () => new Response(JSON.stringify(this.wineBaseEnv)));
		routes.set("/getWineCounter", async () =>
		{
			const wineCounterNum = `${this.wineCounter++}`;
			if(this.wineCounter>9000)
				this.wineCounter = 0;
			return new Response(wineCounterNum);
		});

		this.webServer = webUtil.serve({hostname : WINE_WEB_HOST, port : WINE_WEB_PORT, xlog : this.xlog}, await webUtil.route(routes));

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
		{
			// try gracefully first
			const {timedout} = await runUtil.run("wineboot", ["--end-session", "--shutdown", "--kill", "--force"], {env : this.wineBaseEnv[wineBase], timeout : xu.SECOND*10});
			if(timedout)
			{
				this.xlog.infp`Failed to cleanly stop winebase ${wineBase}, killing it...`;
				await runUtil.run("wineboot", ["--shutdown", "--kill", "--force"], {env : this.wineBaseEnv[wineBase], timeout : xu.SECOND*10});
			}
		}

		for(const p of this.wineserverProcs)
			await runUtil.kill(p);

		this.xlog.debug`Deleting wine prefix bases...`;
		await fileUtil.unlink(WINE_PREFIX, {recursive : true});

		await this.cleanupProcs();

		this.started = false;
	}

	async cleanupProcs()
	{
		this.xlog.info`Killing wine procs...`;
		for(const v of ["winedevice.exe", "services.exe", "explorer.exe", "plugplay.exe", "svchost.exe", "rpcss.exe"])
			await runUtil.run("killall", ["-9", v]);
	}
}
