import {xu} from "xu";
import {Server} from "../Server.js";
import {runUtil, fileUtil} from "xutil";
import {delay} from "https://deno.land/std@0.113.0/async/mod.ts";
import * as path from "https://deno.land/std@0.114.0/path/mod.ts";

const DEBUG = false;	// Set this to true on lostcrag to restrict each VM to just 1 instance and visually show it on screen
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
	win2k    : { extraArgs : ["-nodefaults", "-vga", "cirrus"], extraImgs : ["pagefile.img"] },
	winxp    : { ram : "4G", cores : 8, extraArgs : ["-nodefaults", "-vga", "cirrus"] },
	amigappc : { arch : "ppc", machine : "type=sam460ex", net : "ne2k_pci", hdOpts : ",id=disk", extraArgs : ["-device", "ide-hd,drive=disk,bus=ide.0"], inOutType : "ftp", scriptExt : ".rexx" },
	gentoo   : { arch : "x86_64", ram : "2G", cores : 4, hdOpts : ",if=virtio", net : "virtio-net", extraArgs : ["-device", "virtio-rng-pci"], inOutType : "ssh", scriptExt : ".sh", uefi : true }
};
const SUBNET_ORDER = ["win2k", "winxp", "amigappc", "gentoo"];
Object.keys(OS).sortMulti([v => SUBNET_ORDER.indexOf(v)]).forEach(v => { OS[v].subnet = BASE_SUBNET + SUBNET_ORDER.indexOf(v); });

const UEFI_VARS_SRC_PATH = "/usr/share/edk2-ovmf/OVMF_VARS.fd";
const INSTANCES = {};
const NUM_SERVERS = DEBUG ? 1 : HOSTS[Deno.hostname()]?.numServers || 1;
const RUN_QUEUE = [];
const QEMU_DIR_PATH = path.join(xu.dirname(import.meta), "..", "..", "qemu");

export class qemu extends Server
{
	async start()
	{
		
	}

	status()
	{
		
	}

	stop()
	{
		
	}
}

/*
let serversLaunched = false;

// Called to prepare the QEMU environment for a given OS and then start QEMU
function startOS(osid, instanceid, cb)
{
	if(!INSTANCES[osid])
		INSTANCES[osid] = {};
	
	const instance = {osid, instanceid, dirPath : path.join(C.QEMU_INSTANCE_DIR_PATH, `${osid}-${instanceid}`), ready : false, busy : false};
	instance.debug = DEBUG || OS[osid].debug;
	instance.ip = `192.168.${OS[osid].subnet}.${20+instanceid}`;
	instance.inOutHostPort = +`${OS[osid].subnet}${20+instanceid}`;
	instance.vncPort = ((OS[osid].subnet-BASE_SUBNET)*NUM_SERVERS)+10+instanceid;
	instance.scriptName = `go${OS[osid].scriptExt || OS_DEFAULT.scriptExt}`;
	instance.inOutType = OS[osid].inOutType || OS_DEFAULT.inOutType;
	INSTANCES[osid][instanceid] = instance;
		
	tiptoe(
		function createInstanceDir()
		{
			fs.mkdir(path.join(instance.dirPath, "in"), {recursive : true}, this.parallel());
			fs.mkdir(path.join(instance.dirPath, "out"), {recursive : true}, this.parallel());
		},
		function copyHDImages()
		{
			const imgFilePaths = ["hd.img", ...(OS[osid].extraImgs || [])].map(imgFilename => path.join(C.QEMU_INSTANCE_DIR_PATH, osid, imgFilename));
			imgFilePaths.parallelForEach((imgFilePath, copycb) => fs.copyFile(imgFilePath, path.join(instance.dirPath, path.basename(imgFilePath)), copycb), this.parallel());

			if(OS[osid].uefi)
				fs.copyFile(UEFI_VARS_SRC_PATH, path.join(instance.dirPath, "OVMF_VARS.fd"), this.parallel());
		},
		function runQEMU()
		{
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

			const qemuRunOptions = {silent : true, detached : true, cwd : instance.dirPath};
			if(instance.debug)
				qemuRunOptions.env = {DISPLAY : (os.hostname()==="crystalsummit" ? ":0.1" : ":0")};

			XU.log`QEMU run for osid ${osid}: qemu-system-${OS[osid].arch || OS_DEFAULT.arch} ${qemuArgs}`;

			instance.qemuRunOptions = qemuRunOptions;
			instance.qemuArgs = qemuArgs;
			const instanceJSON = JSON.stringify(instance);

			instance.cp = runUtil.run(`qemu-system-${OS[osid].arch || OS_DEFAULT.arch}`, qemuArgs, qemuRunOptions);
			instance.cp.on("exit", () => { instance.ready = false; instance.cp = null; XU.log`qemu ${osid} #${instanceid} has exited.`; });
			
			XU.log`QEMU ${osid} #${instanceid} [${instance.ip}] launched (VNC port ${5900 + instance.vncPort}), waiting for it to boot...`;

			fs.writeFile(path.join(instance.dirPath, "instance.json"), instanceJSON, XU.UTF8, this);
		},
		cb
	);
}

// Called when the QEMU has fully booted and is ready to received files
function readyOS(osid, instanceid, cb)
{
	const instance = INSTANCES[osid][instanceid];

	tiptoe(
		function mountInOut()
		{
			XU.log`QEMU ${osid} #${instanceid} declared itself ready, mounting in/out...`;

			const mountArgs = ["-t", "cifs", "-o", `user=dexvert,pass=dexvert,port=${instance.inOutHostPort},vers=1.0,sec=ntlm,gid=1000,uid=7777`];
			["in", "out"].serialForEach((v, subcb) => runUtil.run("sudo", ["mount", ...mountArgs, `//127.0.0.1/${v}`, path.join(instance.dirPath, v)], runUtil.SILENT, subcb), this);
		},
		function setInstanceReady()
		{
			XU.log`QEMU ${osid} #${instanceid} fully ready! (VNC ${5900 + instance.vncPort})`;
			instance.ready = true;

			this();
		},
		cb
	);
}

// Called when we need to stop our QEMU OS
function stopOS(osid, instanceid, cb)
{
	const instance = INSTANCES[osid][instanceid];

	tiptoe(
		function unmountInOut()
		{
			XU.log`QEMU stopping ${osid} #${instanceid}... Unmounting in/out...`;
			["in", "out"].serialForEach((v, subcb) => runUtil.run("sudo", ["umount", "-l", path.join(instance.dirPath, v)], runUtil.SILENT, subcb), this);
		},
		function stopQEMU()
		{
			XU.log`QEMU ${osid} #${instanceid} killing qemu child process...`;

			if(instance.cp)
				instance.cp.kill();

			this();
		},
		cb
	);
}

const IN_OUT_LOGIC =
{
	mount : (instance, {body}, cb) =>
	{
		const inDirPath = path.join(instance.dirPath, "in");
		const outDirPath = path.join(instance.dirPath, "out");
		const goFilePath = path.join(inDirPath, instance.scriptName);
		const tmpGoFilePath = fileUtil.generateTempFilePath(undefined, path.extname(instance.scriptName));
		const totalFilesSize = body.inFilePaths.map(inFilePath => fs.statSync(inFilePath).size).sum();

		tiptoe(
			function copyInFiles()
			{
				// We use rsync here to handle both files and directories
				(body.inFilePaths || []).parallelForEach((inFilePath, subcb) => runUtil.run("rsync", ["-aL", inFilePath, path.join(inDirPath, "/")], runUtil.SILENT, subcb), this);
			},
			function waitForInputFiles()
			{
				// If the input file is >50MB then we should wait 1 second PER 50MB to allow the mount to fully catch up
				if(totalFilesSize<DELAY_SIZE)
					return this();
					
				const timeToWait = Math.floor(totalFilesSize/DELAY_SIZE);
				XU.log`QEMU ${instance.osid} #${instance.instanceid} is waiting ${timeToWait} seconds for the mount to fully see the INPUT files due to their large size ${totalFilesSize}`;

				setTimeout(() => this(), timeToWait*XU.SECOND);
			},
			function writeGoScript()
			{
				// We write to a temp file first, and then copy it over in one go to prevent the supervisor from picking up an incomplete file
				fs.writeFile(tmpGoFilePath, body.script, XU.UTF8, this);
			},
			function moveGoScript()
			{
				fileUtil.move(tmpGoFilePath, goFilePath, this);
			},
			function waitForFinish()
			{
				XU.waitUntil(subcb => fileUtil.exists(goFilePath, subcb), exists => !exists, this);
			},
			function waitForOutputFiles()
			{
				// If the input file is >50MB then we should wait 1 second PER 50MB to allow the mount to fully catch up
				if(totalFilesSize<DELAY_SIZE)
					return this();
					
				const timeToWait = Math.floor(totalFilesSize/DELAY_SIZE);
				XU.log`QEMU ${instance.osid} #${instance.instanceid} is waiting ${timeToWait} seconds for the mount to fully see the OUPUT files due to their large size ${totalFilesSize}`;

				setTimeout(() => this(), timeToWait*XU.SECOND);
			},
			function copyResults()
			{
				// We use rsync here to preserve timestamps
				runUtil.run("rsync", ["-aL", path.join(outDirPath, "/"), path.join(body.outDirPath, "/")], runUtil.SILENT, this);
			},
			function cleanFiles()
			{
				fileUtil.emptyDir(inDirPath, this.parallel());
				fileUtil.emptyDir(outDirPath, this.parallel());
			},
			cb
		);
	},
	ftp : (instance, {body}, cb) =>
	{
		const tmpInLHAFilePath = fileUtil.generateTempFilePath(undefined, ".lha");
		const tmpInDirPath = fileUtil.generateTempFilePath();
		const tmpGoFilePath = path.join(tmpInDirPath, instance.scriptName);
		const inLHAFilePath = path.join("/mnt/ram/dexvert/ftp/in", `${instance.ip}.lha`);
		const outLHAFilePath = path.join("/mnt/ram/dexvert/ftp/out", `${instance.ip}.lha`);
		tiptoe(
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
		);
	},
	ssh : (instance, {body}, cb) =>
	{
		const sshOpts = ["-i", path.join(QEMU_DIR_PATH, instance.osid, "dexvert_id_rsa"), "-o", "StrictHostKeyChecking=no", "-p", instance.inOutHostPort];
		const sshPrefix = "dexvert@127.0.0.1";
		const inDirPath = "/in";
		const outDirPath = "/out";
		const goFilePath = path.join(inDirPath, instance.scriptName);
		const tmpGoFilePath = fileUtil.generateTempFilePath(undefined, path.extname(instance.scriptName));

		tiptoe(
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
		);
	}
};


function performRun(instance, runArgs)
{
	const {body, reply} = runArgs;
	XU.log`QEMU ${body.osid} #${instance.instanceid} (VNC ${instance.vncPort}) performing run request: ${{...body, script : body.script.trim().split("\n").find(v => v.startsWith("Run")) || body.script.trim().split("\n")[0]}}`;

	tiptoe(
		function performGoLogic()
		{
			IN_OUT_LOGIC[instance.inOutType](instance, runArgs, this);
		},
		function finishRun(err)
		{
			XU.log`QEMU ${body.osid} #${instance.instanceid} finished request`;
			instance.busy = false;

			reply.send(err ? `error ${err}` : "ok");
		}
	);
}

function checkRunQueue()
{
	if(RUN_QUEUE.length===0)
		return setTimeout(checkRunQueue, 100);
	
	const instance = Object.values(INSTANCES[RUN_QUEUE[0].body?.osid]).find(o => o.ready && !o.busy);
	if(instance)
	{
		instance.busy = true;
		performRun(instance, RUN_QUEUE.shift());
	}

	setTimeout(checkRunQueue, 100);
}

// Starts up our background qemu servers
exports.start = function start(cb)
{
	tiptoe(
		function unmountDeadMounts()
		{
			runUtil.run(path.join(QEMU_DIR_PATH, "unmountDeadMounts.sh"), [], runUtil.SILENT, this);
		},
		function preClean()
		{
			XU.log`QEMU pre-cleaning ${C.QEMU_INSTANCE_DIR_PATH}...`;
			fileUtil.unlink(C.QEMU_INSTANCE_DIR_PATH, this);
		},
		function mkOSInstanceDirs()
		{
			Object.keys(OS).parallelForEach((osid, subcb) => fs.mkdir(path.join(C.QEMU_INSTANCE_DIR_PATH, osid), {recursive : true}, subcb), this);
		},
		function preCopyHDImages()
		{
			XU.log`QEMU pre-copying img files...`;
			Object.entries(OS).parallelForEach(([osid, osInfo], subcb) =>
			{
				const imgFilePaths = ["hd.img", ...(osInfo.extraImgs || [])].map(imgFilename => path.join(QEMU_DIR_PATH, osid, imgFilename));
				imgFilePaths.serialForEach((imgFilePath, copycb) =>
				{
					const imgDestFilePath = path.join(C.QEMU_INSTANCE_DIR_PATH, osid, path.basename(imgFilePath));
					XU.log`QEMU copying to ${imgDestFilePath}...`;
					fs.copyFile(imgFilePath, imgDestFilePath, copycb);
				}, subcb);
			}, this, Object.entries(OS).length);
		},
		function startOSInstances()
		{
			XU.log`QEMU starting instances...`;
			Object.keys(OS).parallelForEach((osid, subcb) => [].pushSequence(0, NUM_SERVERS-1).parallelForEach((instanceid, instancecb) => startOS(osid, instanceid, instancecb), subcb), this);
		},
		function cleanupHDImages()
		{
			Object.keys(OS).parallelForEach((osid, subcb) => fileUtil.unlink(path.join(C.QEMU_INSTANCE_DIR_PATH, osid), subcb), this);
		},
		function startCheckingQueue()
		{
			serversLaunched = true;

			checkRunQueue();
			this();
		},
		cb
	);
};

// The QEMU supervisor.au3 script will call this when it's ready to go
exports.registerRoutes = function registerRoutes(fastify)
{
	fastify.get("/qemuReady", (request, reply) =>
	{
		XU.log`Got /qemuReady request with query: ${request.query}`;
		readyOS(request.query.osid, Object.values(INSTANCES[request.query.osid]).find(v => v.ip===request.query.ip).instanceid, () => reply.send("ok"));
	});
	fastify.post("/qemuRun", (request, reply) => { RUN_QUEUE.push({body : request.body, request, reply}); return undefined; });
};

// Return true if everything is ok
exports.status = function status()
{
	return serversLaunched && Object.values(INSTANCES).flatMap(o => Object.values(o)).every(instance => instance.cp && instance.ready);
};

// Stops our qemu instances
exports.stop = function stop(cb)
{
	tiptoe(
		function killOSes()
		{
			Object.keys(OS).serialForEach((osid, subcb) => [].pushSequence(0, NUM_SERVERS-1).serialForEach((instanceid, instancecb) => stopOS(osid, instanceid, instancecb), subcb), this);
		},
		function waitForKilling()
		{
			XU.waitUntil(subcb => subcb(undefined, Object.values(INSTANCES).flatMap(o => Object.values(o)).some(o => o.ready)), stillReady => stillReady, this);
		},
		cb
	);
};

*/
