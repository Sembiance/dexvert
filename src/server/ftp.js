import {xu} from "xu";
import {Server} from "../Server.js";
import {runUtil} from "xutil";
import {path} from "std";

const FTP_BASE_DIR_PATH = "/mnt/ram/dexvert/ftp";

export class ftp extends Server
{
	vsftpdProc = null;
	baseKeys = Object.keys(this);

	async startVSFTPD()
	{
		this.log`Starting VSFTPD...`;

		const {p} = await runUtil.run("vsftpd", [path.join(xu.dirname(import.meta), "..", "..", "ftp", "amigappc-vsftpd.conf")], {detached : true});
		this.vsftpdProc = p;
		this.vsftpdProc.status().then(async () =>
		{
			this.vsftpdCP = null;

			if(this.stopping)
				return;

			this.log`VSFTPD server has stopped! Restarting...`;
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
		return this.vsftpdProc!==null;
	}

	stop()
	{
		this.log`Stopping VSFTPD...`;
		
		this.stopping = true;

		if(this.vsftpdCP)
			this.vsftpdCP.kill("SIGTERM");
	}
}
