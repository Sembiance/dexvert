import {xu} from "xu";
import {Server} from "../Server.js";
import {runUtil} from "xutil";

export class siegfried extends Server
{
	async start()
	{
		this.xlog.info`Starting siegfried server...`;
		const {p} = await runUtil.run("sf", ["-home", "/opt/siegfried-bin/siegfried/", "-nr", "-serve", "127.0.0.1:15138"], {detached : true, exitcb : async o => await this.exitHandler(o), stdoutcb : line => this.xlog.info`${line}`, stderrcb : line => this.xlog.warn`${line}`});
		this.p = p;
	}

	async exitHandler({success, code, signal})
	{
		if(this.stopping)
			return;

		this.xlog.error`Siegfried server exited unexpectedly (success: ${success}) with code: ${code}, signal: ${signal}`;
		await this.start();
	}

	async status()	// eslint-disable-line require-await
	{
		return !!this.p;
	}

	async stop()
	{
		this.stopping = true;
		await runUtil.kill(this.p);
	}
}
