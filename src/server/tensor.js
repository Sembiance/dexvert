import {xu} from "xu";
import {Server} from "../Server.js";
import {runUtil, fileUtil} from "xutil";
import {TENSORSERV_HOST, TENSORSERV_PORT, TENSORSERV_PATH} from "../tensorUtil.js";
import {path} from "std";

export class tensor extends Server
{
	async start()
	{
		this.xlog.info`Removing existing tensor wip directories...`;
		await fileUtil.unlink(TENSORSERV_PATH, {recursive : true}).catch(() => {});

		this.xlog.info`Creating tensor wip directories...`;
		for(const name of ["__pycache__", "garbage", "tmp"])
			await Deno.mkdir(path.join(TENSORSERV_PATH, name), {recursive : true});

		this.xlog.info`Starting tensor server...`;
		const {p} = await runUtil.run("python", ["-X", `pycache_prefix=${path.join(TENSORSERV_PATH, "__pycache__")}`, "tensorServer.py"], {detached : true, cwd : path.join(xu.dirname(import.meta), "../../tensor")});
		this.p = p;
	}

	async status()
	{
		return this.p && (await (await fetch(`http://${TENSORSERV_HOST}:${TENSORSERV_PORT}/status`).catch(() => {}))?.json())?.status==="a-ok";
	}

	async stop()
	{
		await runUtil.kill(this.p);
	}
}
