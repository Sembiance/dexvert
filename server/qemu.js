"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	os = require("os"),
	fs = require("fs"),
	tiptoe = require("tiptoe"),
	fileUtil = require("@sembiance/xutil").file,
	runUtil = require("@sembiance/xutil").run;

// Set this to true on lostcrag to restrict each VM to just 1 instance and visually show it on screen
const DEBUG = false;
const BASE_SUBNET = 50;
const HOSTS =
{
	lostcrag      : { numServers : 2 },
	crystalsummit : { numServers : 1 },
	chatsubo      : { numServers : 5 }
};

// We specific a given dateTime in order to prevent certain old shareware programs from expiring (Awave Studio)
const OS =
{
	win2k    : { arch : "i386", dateTime : "2021-04-18T10:00:00", subnet : BASE_SUBNET, ram : "1G", machine : "accel=kvm,dump-guest-core=off", hdOpts : ",if=ide,index=0", extraArgs : ["-nodefaults", "-vga", "cirrus"] },
	winxp    : { arch : "i386", dateTime : "2021-04-18T10:00:00", subnet : BASE_SUBNET + 1, ram : "2G", machine : "accel=kvm,dump-guest-core=off", hdOpts : ",if=ide,index=0", cores : 2, extraArgs : ["-nodefaults", "-vga", "cirrus"] },
	amigappc : { arch : "ppc", dateTime : "2021-04-18T10:00:00", subnet : BASE_SUBNET + 2, ram : "1G", machine : "sam460ex", net : "ne2k_pci", hdOpts : ",id=disk", smbGuestPort : 139, extraArgs : ["-device", "ide-hd,drive=disk,bus=ide.0"] }
};

const INSTANCES = {};
const NUM_SERVERS = DEBUG ? 1 : HOSTS[os.hostname()]?.numServers || 1;
const INSTANCE_DIR_PATH = "/mnt/ram/dexvert/qemu";
const RUN_QUEUE = [];
const QEMU_DIR_PATH = path.join(__dirname, "..", "qemu");
let serversLaunched = false;

// Called to prepare the QEMU environment for a given OS and then start QEMU
function startOS(osid, instanceid, cb)
{
	if(!INSTANCES[osid])
		INSTANCES[osid] = {};
	
	const instance = {instanceid, dirPath : path.join(INSTANCE_DIR_PATH, `${osid}-${instanceid}`), ready : false, busy : false};
	instance.debug = DEBUG || OS[osid].debug;
	instance.ip = `192.168.${OS[osid].subnet}.${20+instanceid}`;
	instance.smbHostPort = +`${OS[osid].subnet}${20+instanceid}`;
	instance.vncPort = ((OS[osid].subnet-BASE_SUBNET)*NUM_SERVERS)+10+instanceid;
	INSTANCES[osid][instanceid] = instance;
		
	tiptoe(
		function createInstanceDir()
		{
			fs.mkdir(path.join(instance.dirPath, "in"), {recursive : true}, this.parallel());
			fs.mkdir(path.join(instance.dirPath, "out"), {recursive : true}, this.parallel());
		},
		function copyHDImage()
		{
			fs.copyFile(path.join(INSTANCE_DIR_PATH, `${osid}.img`), path.join(instance.dirPath, "hd.img"), this);
		},
		function runQEMU()
		{
			const qemuArgs = ["-drive", `format=raw,file=hd.img${OS[osid].hdOpts}`];
			if(!instance.debug)
				qemuArgs.push("-nographic", "-vnc", `127.0.0.1:${instance.vncPort}`);
			if(OS[osid].machine)
				qemuArgs.push("-machine", OS[osid].machine);
			qemuArgs.push("-m", `size=${OS[osid].ram}`);
			qemuArgs.push("-rtc", `base=${OS[osid].dateTime}`);
			if((OS[osid].cores || 1)>1)
				qemuArgs.push("-smp", `cores=${OS[osid].cores}`);
			qemuArgs.push("-netdev", `user,net=192.168.${OS[osid].subnet}.0/24,dhcpstart=${instance.ip},hostfwd=tcp:127.0.0.1:${instance.smbHostPort}-${instance.ip}:${OS[osid].smbGuestPort || 445},id=nd1`);
			qemuArgs.push("-device", `${OS[osid].net || "rtl8139"},netdev=nd1`);
			qemuArgs.push(...OS[osid].extraArgs || []);

			const qemuRunOptions = {silent : true, detached : true, cwd : instance.dirPath};
			if(instance.debug)
			{
				qemuRunOptions.env = {DISPLAY : (os.hostname()==="crystalsummit" ? ":0.1" : ":0")};
				XU.log`QEMU args for osid: ${qemuArgs}`;
			}

			instance.cp = runUtil.run(`qemu-system-${OS[osid].arch}`, qemuArgs, qemuRunOptions);
			instance.cp.on("exit", () => { instance.ready = false; instance.cp = null; XU.log`qemu ${osid} #${instanceid} has exited.`; });
			
			XU.log`QEMU ${osid} #${instanceid} [${instance.ip}] launched (VNC port ${5900 + instance.vncPort}), waiting for it to boot...`;

			setImmediate(this);
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
			if(instance.debug)
				XU.log`QEMU ${osid} #${instanceid} declared itself ready, mounting in/out...`;

			const mountArgs = ["-t", "cifs", "-o", `user=dexvert,pass=dexvert,port=${instance.smbHostPort},vers=1.0,sec=ntlm,gid=1000,uid=7777`];
			["in", "out"].serialForEach((v, subcb) => runUtil.run("sudo", ["mount", ...mountArgs, `//127.0.0.1/${v}`, path.join(instance.dirPath, v)], runUtil.SILENT, subcb), this);
		},
		function setInstanceReady()
		{
			XU.log`QEMU ${osid} #${instanceid} fully ready!`;
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

function performRun(instance, {body, reply})
{
	XU.log`QEMU ${body.osid} #${instance.instanceid} (VNC ${instance.vncPort}) performing run request: ${{...body, script : body.script.trim().split("\n").find(v => v.startsWith("Run") || body.script.trim().split("\n")[0])}}`;

	const inDirPath = path.join(instance.dirPath, "in");
	const outDirPath = path.join(instance.dirPath, "out");
	const scriptExt = body.osid.startsWith("win") ? ".au3" : ".script";
	const goFilePath = path.join(inDirPath, `go${scriptExt}`);
	const tmpGoFilePath = fileUtil.generateTempFilePath(undefined, scriptExt);

	tiptoe(
		function copyInFiles()
		{
			// We use rsync here to handle both files and directories
			(body.inFilePaths || []).parallelForEach((inFilePath, subcb) => runUtil.run("rsync", ["-aL", inFilePath, path.join(inDirPath, "/")], runUtil.SILENT, subcb), this);
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
			XU.log`QEMU pre-cleaning ${INSTANCE_DIR_PATH}...`;
			fileUtil.unlink(INSTANCE_DIR_PATH, this);
		},
		function mkInstanceDir()
		{
			fs.mkdir(INSTANCE_DIR_PATH, {recursive : true}, this);
		},
		function preCopyHDImages()
		{
			XU.log`QEMU Copying hd img files...`;
			Object.keys(OS).parallelForEach((osid, subcb) => fs.copyFile(path.join(QEMU_DIR_PATH, osid, "hd.img"), path.join(INSTANCE_DIR_PATH, `${osid}.img`), subcb), this);
		},
		function startOSInstances()
		{
			XU.log`QEMU starting instances...`;
			Object.keys(OS).parallelForEach((osid, subcb) => [].pushSequence(0, NUM_SERVERS-1).parallelForEach((instanceid, instancecb) => startOS(osid, instanceid, instancecb), subcb), this);
		},
		function cleanupHDImages()
		{
			Object.keys(OS).parallelForEach((osid, subcb) => fileUtil.unlink(path.join(INSTANCE_DIR_PATH, `${osid}.img`), subcb), this);
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

// Stops our unoconv background server
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
