import {xu} from "xu";
import {Server} from "../Server.js";
import {runUtil, fileUtil} from "xutil";
import {TENSORSERV_HOST, TENSORSERV_PORT, TENSORSERV_PATH} from "../tensorUtil.js";
import {path} from "std";

export class tensor extends Server
{
	async start()
	{
		const SRC_DIR = path.join(xu.dirname(import.meta), "../../tensor");
		const WIP_DIR = TENSORSERV_PATH;

		this.xlog.info`Stopping previous tensor server docker...`;
		await runUtil.run("docker", ["stop", "dexvert-tensor"]);

		this.xlog.info`Removing existing tensor wip directories...`;
		await fileUtil.unlink(WIP_DIR, {recursive : true}).catch(() => {});

		this.xlog.info`Creating tensor wip directories...`;
		for(const name of ["__pycache__", "garbage", "tmp"])
			await Deno.mkdir(path.join(WIP_DIR, name), {recursive : true});

		this.xlog.info`Copying tensor files...`;
		for(const name of ["tensorServer.sh", "tensorServer.py", "TensorModel.py", "garbage/model/"])
		{
			const targetPath = path.join(WIP_DIR, name);
			await Deno.mkdir(path.dirname(targetPath), {recursive : true});
			await runUtil.run("rsync", ["-sal", path.join(SRC_DIR, name), targetPath]);
		}

		this.xlog.info`Running tensor server docker...`;
		const hasGPU = ["lostcrag", "chatsubo"].includes(Deno.hostname());
		const tensorDockerTag = hasGPU ? "tensorflow/tensorflow:latest-gpu" : "tensorflow/tensorflow";
		const tensorGPUArgs = hasGPU ? ["--gpus", "all"] : [];
		const dockerArgs = ["run", "--name", "dexvert-tensor", ...tensorGPUArgs, "--rm", "-p", `${TENSORSERV_HOST}:${TENSORSERV_PORT}:${TENSORSERV_PORT}`, "-v", `${WIP_DIR}:${WIP_DIR}`, "-w", WIP_DIR, tensorDockerTag, "./tensorServer.sh"];
		await runUtil.run("docker", dockerArgs, {verbose : true, detached : true, stdoutcb : line => this.xlog.info`${line}`, stderrcb : line => this.xlog.warn`${line}`, cwd : WIP_DIR});
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
