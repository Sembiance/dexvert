import {xu} from "xu";
import {Server} from "../Server.js";
import {runUtil} from "xutil";
import {path} from "std";

const FTP_BASE_DIR_PATH = "/mnt/ram/dexvert/ftp";

export class ftp extends Server
{
	p = null;
	baseKeys = Object.keys(this);

	async startUFTPD()
	{
		this.xlog.info`Stopping existing UFTPD procs...`;
		await runUtil.run("sudo", ["killall", "--wait", "uftpd"]);

		this.xlog.info`Starting UFTPD...`;

		const {p} = await runUtil.run("uftpd", ["-n", "-o", `ftp=7021,tftp=0,pasv_addr=192.168.52.2,writable`, FTP_BASE_DIR_PATH], {detached : true, stdoutcb : line => this.xlog.info`${line}`, stderrcb : line => this.xlog.warn`${line}`});
		this.p = p;
		this.p.status().then(async () =>
		{
			this.p = null;

			if(this.stopping)
				return;

			this.xlog.error`UFTPD server has stopped! Restarting...`;
			await this.startUFTPD();
		});
	}

	async start()
	{
		for(const v of ["in", "out", "backup"])
			await Deno.mkdir(path.join(FTP_BASE_DIR_PATH, v), {recursive : true});

		await this.startUFTPD();
	}

	status()
	{
		return this.p!==null;
	}

	async stop()
	{
		this.xlog.info`Stopping UFTPD...`;
		
		this.stopping = true;

		if(this.p)
			await runUtil.kill(this.p);
	}
}
