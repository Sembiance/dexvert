import {xu} from "xu";
import {Server} from "../Server.js";
import {runUtil, fileUtil} from "xutil";
import {TENSORSERV_HOST, TENSORSERV_PORT, TENSORSERV_PATH} from "../tensorUtil.js";
import * as path from "https://deno.land/std@0.111.0/path/mod.ts";
import * as fs from "https://deno.land/std@0.111.0/fs/mod.ts";

export class tensor extends Server
{
	async start()
	{
		await Deno.mkdir("/mnt/dexvert/garbageDetected", {recursive : true});

		const SRC_DIR = path.join(xu.dirname(import.meta), "../../tensor");
		const WIP_DIR = TENSORSERV_PATH;

		xu.log`Removing existing tensor wip directories...`;
		await fileUtil.unlink(WIP_DIR, {recursive : true}).catch(() => {});

		xu.log`Creating tensor wip directories...`;
		for(const name of ["__pycache__", "garbage", "tmp"])
			await Deno.mkdir(path.join(WIP_DIR, name), {recursive : true});

		xu.log`Copying tensor files...`;
		for(const name of ["tensorServer.sh", "tensorServer.py", "TensorModel.py", "garbage/model"])
			await fs.copy(path.join(SRC_DIR, Array.isArray(name) ? name[0] : name), path.join(WIP_DIR, Array.isArray(name) ? name[1] : name));

		xu.log`Running tensor server docker...`;
		const dockerArgs = ["run", "--name", "dexvert-tensor", "--gpus", "all", "--rm", "-p", `${TENSORSERV_HOST}:${TENSORSERV_PORT}:${TENSORSERV_PORT}`, "-v", `${WIP_DIR}:${WIP_DIR}`, "-w", WIP_DIR, "tensorflow/tensorflow:latest-gpu", "./tensorServer.sh"];
		await runUtil.run("docker", dockerArgs, {detached : true, liveOutput : true, cwd : WIP_DIR});
	}

	async status()
	{
		return (await (await fetch(`http://${TENSORSERV_HOST}:${TENSORSERV_PORT}/status`).catch(() => {}))?.json())?.status==="a-ok";
	}

	async stop()
	{
		await runUtil.run("docker", ["stop", "dexvert-tensor"]);
	}
}
