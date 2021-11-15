import {xu} from "xu";
import {Server} from "../Server.js";
import {runUtil, fileUtil} from "xutil";
import {delay} from "https://deno.land/std@0.113.0/async/mod.ts";

export class xdisplay extends Server
{
	async start()
	{
		// If we don't have a DISPLAY variable, start up a background X display
		if(Deno.env.get("DISPLAY"))
		{
			xu.log`X DISPLAY already exists!`;
			return;
		}

		const {p} = await runUtil.run("X", [], {detached : true, liveOutput : true});
		this.xProc = p;
		await xu.waitUntil(async () => await fileUtil.exists("/tmp/.X0-lock"));
		await delay(xu.SECOND*2);
		await runUtil.run("dbus-launch", ["--exit-with-x11"], {env : {DISPLAY : ":0", detached : true, liveOutput : true}});
	}

	status()
	{
		return true;
	}

	stop()
	{
		if(this.xProc)
			this.xProc.kill("SIGTERM");
	}
}
