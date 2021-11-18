import {xu, fg} from "xu";
import {Server} from "../Server.js";
import {runUtil, fileUtil} from "xutil";
import {path, delay} from "std";
import {WebServer} from "WebServer";
import {QEMU_SERVER_HOST, QEMU_SERVER_PORT} from "../qemuUtil.js";

const QEMU_INSTANCE_DIR_PATH = "/mnt/dexvert/qemu";
const DEBUG = true;	// Set this to true on lostcrag to restrict each VM to just 1 instance and visually show it on screen
const BASE_SUBNET = 50;
const DELAY_SIZE = xu.MB*50;
const HOSTS =
{
	lostcrag      : { numServers :  2 },
	crystalsummit : { numServers :  1 },
	chatsubo      : { numServers : 10 }
};
const OS_DEFAULT =
{
	arch         : "i386",
	dateTime     : "2021-04-18T10:00:00",
	ram          : "1G",
	smbGuestPort : 445,
	sshGuestPort : 22,
	inOutType    : "mount",
	scriptExt    : ".au3",
	machine      : "accel=kvm",
	hdOpts       : ",if=ide"
};

// We specific a given dateTime in order to prevent certain old shareware programs from expiring (Awave Studio)
const OS =
{
	win2k    : { extraArgs : ["-nodefaults", "-vga", "cirrus"], extraImgs : ["pagefile.img"] }//,
	//winxp    : { ram : "4G", cores : 8, extraArgs : ["-nodefaults", "-vga", "cirrus"] },
	//amigappc : { arch : "ppc", machine : "type=sam460ex", net : "ne2k_pci", hdOpts : ",id=disk", extraArgs : ["-device", "ide-hd,drive=disk,bus=ide.0"], inOutType : "ftp", scriptExt : ".rexx" },
	//gentoo   : { arch : "x86_64", ram : "2G", cores : 4, hdOpts : ",if=virtio", net : "virtio-net", extraArgs : ["-device", "virtio-rng-pci"], inOutType : "ssh", scriptExt : ".sh", uefi : true }
};
const SUBNET_ORDER = ["win2k", "winxp", "amigappc", "gentoo"];
Object.keys(OS).sortMulti([v => SUBNET_ORDER.indexOf(v)]).forEach(v => { OS[v].subnet = BASE_SUBNET + SUBNET_ORDER.indexOf(v); });

const UEFI_VARS_SRC_PATH = "/usr/share/edk2-ovmf/OVMF_VARS.fd";
const INSTANCES = {};
const NUM_SERVERS = DEBUG ? 1 : HOSTS[Deno.hostname()]?.numServers || 1;
const RUN_QUEUE = [];
const QEMU_DIR_PATH = path.join(xu.dirname(import.meta), "..", "..", "qemu");

const IN_OUT_LOGIC =
{
	mount : async (instance, {body}) =>
	{
		const inDirPath = path.join(instance.dirPath, "in");
		const outDirPath = path.join(instance.dirPath, "out");
		const goFilePath = path.join(inDirPath, instance.scriptName);
		const tmpGoFilePath = await fileUtil.genTempPath(undefined, path.extname(instance.scriptName));
		const totalFilesSize = (await body.inFilePaths.parallelMap(async inFilePath => (await Deno.stat(inFilePath)).size)).sum();

		// We use rsync here to handle both files and directories
		await (body.inFilePaths || []).parallelMap(async inFilePath => await runUtil.run("rsync", ["-aL", inFilePath, path.join(inDirPath, "/")]));

		// If the input file is >50MB then we should wait 1 second PER 50MB to allow the mount to fully catch up
		if(totalFilesSize>=DELAY_SIZE)
		{
			const timeToWait = Math.floor(totalFilesSize/DELAY_SIZE);
			this.log`${instance.osid} #${instance.instanceid} is waiting ${timeToWait} seconds for the mount to fully see the INPUT files due to their large size ${totalFilesSize.bytesToSize()}`;
			await delay(timeToWait*xu.SECOND);
		}

		// We write to a temp file first, and then copy it over in one go to prevent the supervisor from picking up an incomplete file
		await fileUtil.writeFile(tmpGoFilePath, body.script);
		await fileUtil.move(tmpGoFilePath, goFilePath, this);

		// Wait for finish, which happens when the VM deletes the go file
		await xu.waitUntil(async () => (!(await fileUtil.exists(goFilePath))));

		// If the input file was >50MB then we should wait 1 second PER 50MB to allow the output files on the mount to fully catch up
		if(totalFilesSize>=DELAY_SIZE)
		{
			const timeToWait = Math.floor(totalFilesSize/DELAY_SIZE);
			this.log`${instance.osid} #${instance.instanceid} is waiting ${timeToWait} seconds for the mount to fully see the OUPUT files due to their large size ${totalFilesSize.bytesToSize()}`;
			await delay(timeToWait*xu.SECOND);
		}

		// We use rsync here to preserve timestamps
		await runUtil.run("rsync", ["-a", path.join(outDirPath, "/"), path.join(body.outDirPath, "/")]);

		await fileUtil.emptyDir(inDirPath);
		await fileUtil.emptyDir(outDirPath);
	},
	ftp : async (instance, {body}) =>
	{
		const tmpInLHAFilePath = await fileUtil.genTempPath(undefined, ".lha");
		const tmpInDirPath = await fileUtil.genTempPath();
		const tmpGoFilePath = path.join(tmpInDirPath, instance.scriptName);
		const inLHAFilePath = path.join("/mnt/ram/dexvert/ftp/in", `${instance.ip}.lha`);
		const outLHAFilePath = path.join("/mnt/ram/dexvert/ftp/out", `${instance.ip}.lha`);
		/*tiptoe(
			function createTmpInDirPath()
			{
				fs.mkdir(tmpInDirPath, {recursive : true}, this);
			},
			function prepareInFiles()
			{
				// We use rsync here to handle both files and directories
				(body.inFilePaths || []).parallelForEach((inFilePath, subcb) => runUtil.run("rsync", ["-aL", inFilePath, path.join(tmpInDirPath, "/")], runUtil.SILENT, subcb), this.parallel());

				fs.writeFile(tmpGoFilePath, body.script, XU.UTF8, this.parallel());
			},
			function createInLHA()
			{
				// We create to a temp file first, and then copy it over in one go to prevent the supervisor from picking up an incomplete file
				runUtil.run("lha", ["c", tmpInLHAFilePath, "*"], {silent : true, shell : "/bin/bash", cwd : tmpInDirPath}, this);
			},
			function moveInLHA()
			{
				fileUtil.move(tmpInLHAFilePath, inLHAFilePath, this);
			},
			function waitForFinish()
			{
				XU.waitUntil(subcb => fileUtil.exists(inLHAFilePath, subcb), exists => !exists, this);
			},
			function extractrResults()
			{
				runUtil.run("lha", ["-x", `-w=${body.outDirPath}`, outLHAFilePath], runUtil.SILENT, this);
			},
			function cleanFiles()
			{
				fileUtil.unlink(tmpInDirPath, this.parallel());
				fileUtil.unlink(outLHAFilePath, this.parallel());
			},
			cb
		);*/
	},
	ssh : async (instance, {body}) =>
	{
		const sshOpts = ["-i", path.join(QEMU_DIR_PATH, instance.osid, "dexvert_id_rsa"), "-o", "StrictHostKeyChecking=no", "-p", instance.inOutHostPort];
		const sshPrefix = "dexvert@127.0.0.1";
		const inDirPath = "/in";
		const outDirPath = "/out";
		const goFilePath = path.join(inDirPath, instance.scriptName);
		const tmpGoFilePath = await fileUtil.genTempPath(undefined, path.extname(instance.scriptName));

		/*tiptoe(
			function copyInFiles()
			{
				// We use rsync here to handle both files and directories
				(body.inFilePaths || []).parallelForEach((inFilePath, subcb) => runUtil.run("rsync", ["-aL", "-e", `ssh ${sshOpts.join(" ")}`, inFilePath, path.join(`${sshPrefix}:${inDirPath}`, "/")], runUtil.SILENT, subcb), this);
			},
			function writeGoScript()
			{
				// We write to a temp file first, and then copy it over in one go to prevent the supervisor from picking up an incomplete file
				fs.writeFile(tmpGoFilePath, body.script, XU.UTF8, this);
			},
			function copyGoScript()
			{
				runUtil.run("scp", [...sshOpts.map(v => (v==="-p" ? "-P" : v)), tmpGoFilePath, `${sshPrefix}:${goFilePath}`], runUtil.SILENT, this);
			},
			function waitForFinish()
			{
				XU.waitUntil(subcb => runUtil.run("ssh", [...sshOpts, sshPrefix, "ls", goFilePath], runUtil.SILENT, subcb), outRaw => (outRaw && outRaw.trim()!==goFilePath), this);
			},
			function copyResults()
			{
				// We use rsync here to preserve timestamps
				runUtil.run("rsync", ["-aL", "-e", `ssh ${sshOpts.join(" ")}`, path.join(`${sshPrefix}:${outDirPath}`, "/"), path.join(body.outDirPath, "/")], runUtil.SILENT, this);
			},
			function cleanFiles()
			{
				fileUtil.unlink(tmpGoFilePath, this.parallel());
				runUtil.run("ssh", [...sshOpts, sshPrefix, "rm", "-rf", path.join(inDirPath, "*")], runUtil.SILENT, this.parallel());
				runUtil.run("ssh", [...sshOpts, sshPrefix, "rm", "-rf", path.join(outDirPath, "*")], runUtil.SILENT, this.parallel());
			},
			cb
		);*/
	}
};

export class qemu extends Server
{
	serversLaunched = false;
	baseKeys = Object.keys(this);

	// Called to prepare the QEMU environment for a given OS and then start QEMU
	async startOS(osid, instanceid)
	{
		if(!INSTANCES[osid])
			INSTANCES[osid] = {};
		
		const instance = {osid, instanceid, dirPath : path.join(QEMU_INSTANCE_DIR_PATH, `${osid}-${instanceid}`), ready : false, busy : false};
		instance.debug = DEBUG || OS[osid].debug;
		instance.ip = `192.168.${OS[osid].subnet}.${20+instanceid}`;
		instance.inOutHostPort = +`${OS[osid].subnet}${20+instanceid}`;
		instance.vncPort = ((OS[osid].subnet-BASE_SUBNET)*NUM_SERVERS)+10+instanceid;
		instance.scriptName = `go${OS[osid].scriptExt || OS_DEFAULT.scriptExt}`;
		instance.inOutType = OS[osid].inOutType || OS_DEFAULT.inOutType;
		INSTANCES[osid][instanceid] = instance;
		
		await Deno.mkdir(path.join(instance.dirPath, "in"), {recursive : true});
		await Deno.mkdir(path.join(instance.dirPath, "out"), {recursive : true});

		const imgFilePaths = ["hd.img", ...(OS[osid].extraImgs || [])].map(imgFilename => path.join(QEMU_INSTANCE_DIR_PATH, osid, imgFilename));
		await imgFilePaths.parallelMap(imgFilePath => Deno.copyFile(imgFilePath, path.join(instance.dirPath, path.basename(imgFilePath))));
		if(OS[osid].uefi)
			await Deno.copyFile(UEFI_VARS_SRC_PATH, path.join(instance.dirPath, "OVMF_VARS.fd"));

		const qemuArgs = ["-drive", `format=raw,file=hd.img${OS[osid].hdOpts || OS_DEFAULT.hdOpts}`];
		if(!instance.debug)
			qemuArgs.push("-nographic", "-vnc", `127.0.0.1:${instance.vncPort}`);
		qemuArgs.push("-machine", `${OS[osid].machine || OS_DEFAULT.machine},dump-guest-core=off`);
		qemuArgs.push("-m", `size=${OS[osid].ram || OS_DEFAULT.ram}`);
		qemuArgs.push("-rtc", `base=${OS[osid].dateTime || OS_DEFAULT.dateTime}`);
		if((OS[osid].cores || 1)>1)
			qemuArgs.push("-smp", `cores=${OS[osid].cores}`);
		
		let netDevVal = `user,net=192.168.${OS[osid].subnet}.0/24,dhcpstart=${instance.ip},id=nd1`;
		if(instance.inOutType==="mount")
			netDevVal += `,hostfwd=tcp:127.0.0.1:${instance.inOutHostPort}-${instance.ip}:${OS[osid].smbGuestPort || OS_DEFAULT.smbGuestPort}`;
		else if(instance.inOutType==="ssh")
			netDevVal += `,hostfwd=tcp:127.0.0.1:${instance.inOutHostPort}-${instance.ip}:${OS[osid].sshGuestPort || OS_DEFAULT.sshGuestPort}`;
		qemuArgs.push("-netdev", netDevVal);

		qemuArgs.push("-device", `${OS[osid].net || "rtl8139"},netdev=nd1`);

		(OS[osid].extraImgs || []).forEach(extraImg => qemuArgs.push("-drive", `format=raw,file=${extraImg}${OS[osid].hdOpts || OS_DEFAULT.hdOpts}`));

		if(OS[osid].uefi)
		{
			qemuArgs.push("-drive", "if=pflash,format=raw,unit=0,file=/usr/share/edk2-ovmf/OVMF_CODE.fd,readonly=on");
			qemuArgs.push("-drive", "if=pflash,format=raw,unit=1,file=OVMF_VARS.fd");
		}

		qemuArgs.push(...OS[osid].extraArgs || []);

		const qemuRunOptions = {detached : true, cwd : instance.dirPath};
		if(instance.debug)
			qemuRunOptions.env = {DISPLAY : (Deno.hostname()==="crystalsummit" ? ":0.1" : ":0")};

		this.log`Launching ${osid} #${instanceid}: qemu-system-${OS[osid].arch || OS_DEFAULT.arch} ${xu.inspect(qemuArgs).squeeze()} and options ${xu.inspect(qemuRunOptions).squeeze()}`;

		instance.qemuRunOptions = qemuRunOptions;
		instance.qemuArgs = qemuArgs;
		const instanceJSON = JSON.stringify(instance);
		const {p} = await runUtil.run(`qemu-system-${OS[osid].arch || OS_DEFAULT.arch}`, qemuArgs, qemuRunOptions);
		instance.p = p;
		instance.p.status().then(v =>
		{
			instance.ready = false;
			instance.p = null;
			this.log`${osid} #${instanceid} has exited with status ${v}`;
		});

		this.log`${osid} #${instanceid} [${instance.ip}] launched (VNC port ${5900 + instance.vncPort}), waiting for it to boot...`;
		await fileUtil.writeFile(path.join(instance.dirPath, "instance.json"), instanceJSON);
	}

	// Called when the QEMU has fully booted and is ready to received files
	async readyOS(instance)
	{
		this.log`${instance.osid} #${instance.instanceid} declared itself ready, mounting in/out...`;
		if(instance.inOutType==="mount")
		{
			const mountArgs = ["-t", "cifs", "-o", `user=dexvert,pass=dexvert,port=${instance.inOutHostPort},vers=1.0,sec=ntlm,gid=1000,uid=7777`];
			for(const v of ["in", "out"])
				await runUtil.run("sudo", ["mount", ...mountArgs, `//127.0.0.1/${v}`, path.join(instance.dirPath, v)]);
		}

		this.log`${instance.osid} #${instance.instanceid} fully ready! (VNC ${5900 + instance.vncPort})`;
		instance.ready = true;
	}

	async performRun(instance, runArgs)
	{
		const {body, reply} = runArgs;
		this.log`${body.osid} #${instance.instanceid} (VNC ${instance.vncPort}) performing run request: ${{...body, script : body.script.trim().split("\n").find(v => v.startsWith("Run")) || body.script.trim().split("\n")[0]}}`;

		let inOutErr = null;
		await IN_OUT_LOGIC[instance.inOutType](instance, runArgs).catch(err => { inOutErr = err; });
		this.log`${body.osid} #${instance.instanceid} finished request`;
		instance.busy = false;

		reply(new Response(inOutErr ? inOutErr.toString() : "ok"));
	}

	checkRunQueue()
	{
		if(RUN_QUEUE.length===0)
			return setTimeout(() => this.checkRunQueue(), 100);
		
		const instance = Object.values(INSTANCES[RUN_QUEUE[0].body?.osid]).find(o => o.ready && !o.busy);
		if(instance)
		{
			instance.busy = true;
			this.performRun(instance, RUN_QUEUE.shift());
		}

		setTimeout(() => this.checkRunQueue(), 100);
	}

	async start()
	{
		this.webServer = WebServer.create(QEMU_SERVER_HOST, QEMU_SERVER_PORT);
		this.webServer.add("/qemuReady", async request =>
		{
			const u = new URL(request.url);
			const body = Object.fromEntries(["osid", "ip"].map(k => ([k, u.searchParams.get(k)])));
			this.log`Got qemuReady request from ${fg.peach(body.osid)}${fg.cyan("@")}${fg.yellow(body.ip)}`;
			await this.readyOS(Object.values(INSTANCES[body.osid]).find(v => v.ip===body.ip));
			return new Response("ok");
		});
		this.webServer.add("/qemuRun", async (request, reply) =>
		{
			const body = await request.json();
			this.log`Got qemuRun request for ${body.osid}`;
			RUN_QUEUE.push({body, request, reply});
		}, {detached : true, method : "POST"});
		await this.webServer.start();

		await runUtil.run(path.join(QEMU_DIR_PATH, "unmountDeadMounts.sh"), []);

		this.log`Pre-cleaning ${QEMU_INSTANCE_DIR_PATH}`;
		await fileUtil.unlink(QEMU_INSTANCE_DIR_PATH, {recursive : true});

		for(const osid of Object.keys(OS))
			await Deno.mkdir(path.join(QEMU_INSTANCE_DIR_PATH, osid), {recursive : true});

		this.log`Pre-copying img files...`;
		for(const [osid, osInfo] of Object.entries(OS))
		{
			for(const imgFilePath of ["hd.img", ...(osInfo.extraImgs || [])].map(imgFilename => path.join(QEMU_DIR_PATH, osid, imgFilename)))
			{
				const imgDestFilePath = path.join(QEMU_INSTANCE_DIR_PATH, osid, path.basename(imgFilePath));
				this.log`Copying to: ${imgDestFilePath}`;
				await Deno.copyFile(imgFilePath, imgDestFilePath);
			}
		}

		this.log`Starting instances...`;
		await Object.keys(OS).parallelMap(osid => [].pushSequence(0, NUM_SERVERS-1).parallelMap(instanceid => this.startOS(osid, instanceid)));

		this.log`Cleaning up HD images...`;
		for(const osid of Object.keys(OS))
			await fileUtil.unlink(path.join(QEMU_INSTANCE_DIR_PATH, osid), {recursive : true});

		this.serversLaunched = true;
		this.checkRunQueue();
	}

	status()
	{
		const instances = Object.values(INSTANCES).flatMap(o => Object.values(o));
		return this.serversLaunched && instances.length>0 && instances.every(instance => instance.p && instance.ready);
	}

	async stopOS(instance)
	{
		this.log`Stopping ${instance.osid} #${instance.instanceid}...`;
		if(instance.inOutType==="mount")
		{
			this.log`${instance.osid} #${instance.instanceid} unmounting in/out...`;
			for(const v of ["in", "out"])
				await runUtil.run("sudo", ["umount", "-l", path.join(instance.dirPath, v)]);
		}

		this.log`${instance.osid} #${instance.instanceid} killing qemu child process...`;
		if(instance.p)
			instance.p.kill("SIGTERM");
	}

	async stop()
	{
		if(this.webServer)
			this.webServer.stop();
		
		for(const instance of Object.values(INSTANCES).flatMap(o => Object.values(o)))
			await this.stopOS(instance);
	}
}
