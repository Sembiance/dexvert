import {xu} from "xu";
import {Server} from "../Server.js";
import {runUtil, fileUtil} from "xutil";
import {CLASSIFY_HOST, CLASSIFY_PORT, CLASSIFY_PATH} from "../classifyUtil.js";
import {path} from "std";

export class classify extends Server
{
	async start()
	{
		this.xlog.info`Removing existing classify wip directories...`;
		await fileUtil.unlink(CLASSIFY_PATH, {recursive : true}).catch(() => {});

		this.xlog.info`Creating classify wip directories...`;
		for(const name of ["__pycache__", "garbage", "tmp"])
			await Deno.mkdir(path.join(CLASSIFY_PATH, name), {recursive : true});

		this.xlog.info`Starting classify server...`;
		const classifyDirPath = path.join(import.meta.dirname, "..", "..", "classify");
		const runOptions = {detached : true, cwd : classifyDirPath, env : {VIRTUAL_ENV : path.join(classifyDirPath, "env")}};
		const {p} = await runUtil.run(path.join(classifyDirPath, "env/bin/python3"), ["-X", `pycache_prefix=${path.join(CLASSIFY_PATH, "__pycache__")}`, "classifyServer.py"], runOptions);
		this.p = p;
	}

	async status()
	{
		return this.p && (await (await fetch(`http://${CLASSIFY_HOST}:${CLASSIFY_PORT}/status`).catch(() => {}))?.json())?.status==="a-ok";
	}

	async stop()
	{
		await runUtil.kill(this.p);
	}
}
