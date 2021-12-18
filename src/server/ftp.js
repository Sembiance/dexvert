import {xu} from "xu";
import {Server} from "../Server.js";
import {runUtil} from "xutil";
import {path} from "std";

const FTP_BASE_DIR_PATH = "/mnt/ram/dexvert/ftp";

export class ftp extends Server
{
	p = null;
	baseKeys = Object.keys(this);

	async startVSFTPD()
	{
		this.xlog.info`Stopping existing VSFTPD procs...`;
		await runUtil.run("sudo", ["killall", "--wait", "vsftpd"]);

		this.xlog.info`Starting VSFTPD...`;

		const {p} = await runUtil.run("vsftpd", [path.join(xu.dirname(import.meta), "..", "..", "ftp", "amigappc-vsftpd.conf")], {detached : true});
		this.p = p;
		this.p.status().then(async () =>
		{
			this.p = null;

			if(this.stopping)
				return;

			this.xlog.warn`VSFTPD server has stopped! Restarting...`;
			await this.startVSFTPD();
		});
	}

	async start()
	{
		for(const v of ["in", "out", "backup"])
			await Deno.mkdir(path.join(FTP_BASE_DIR_PATH, v), {recursive : true});

		await this.startVSFTPD();
	}

	status()
	{
		return this.p!==null;
	}

	async stop()
	{
		this.xlog.info`Stopping VSFTPD...`;
		
		this.stopping = true;

		if(this.p)
			await runUtil.kill(this.p, "SIGTERM");
	}
}
