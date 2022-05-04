import {xu} from "xu";
import {Server} from "../Server.js";
import {runUtil} from "xutil";

export class siegfried extends Server
{
	async start()
	{
		this.xlog.info`Starting siegfried server...`;
		const {p} = await runUtil.run("sf", ["-home", "/opt/siegfried-bin/siegfried/", "-nr", "-serve", "127.0.0.1:15138"], {detached : true});
		this.p = p;
	}

	async status()	// eslint-disable-line require-await
	{
		return !!this.p;
	}

	async stop()
	{
		await runUtil.kill(this.p);
	}
}
