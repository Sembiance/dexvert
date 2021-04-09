"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	fs = require("fs"),
	tiptoe = require("tiptoe"),
	fileUtil = require("@sembiance/xutil").file,
	runUtil = require("@sembiance/xutil").run;

// Set this to true on lostcrag to restrict each VM to just 1 instance and visually show it on screen
const DEBUG = false;

const OS =
{
	win2k : { arch : "i386", subnet : 50, ram : "1G" },
	winxp : { arch : "i386", subnet : 51, ram : "2G", cores : 2 }
};

const INSTANCES = {};
const NUM_SERVERS = DEBUG ? 1 : 5;
const INSTANCE_DIR_PATH = "/mnt/ram/dexvert/qemu";
const RUN_QUEUE = [];

// Called to prepare the QEMU environment for a given OS and then start QEMU
function startOS(osid, instanceid, cb)
{
	if(!INSTANCES[osid])
		INSTANCES[osid] = {};
	
	const instance = {instanceid, dirPath : path.join(INSTANCE_DIR_PATH, `${osid}-${instanceid}`), ready : false, busy : false};
	instance.ip = `192.168.${OS[osid].subnet}.${20+instanceid}`;
	instance.smbPort = +`${OS[osid].subnet}${20+instanceid}`;
	INSTANCES[osid][instanceid] = instance;
		
	tiptoe(
		function createInstanceDir()
		{
			fs.mkdir(path.join(instance.dirPath, "in"), {recursive : true}, this.parallel());
			fs.mkdir(path.join(instance.dirPath, "out"), {recursive : true}, this.parallel());
		},
		function copyHDImage()
		{
			XU.log`QEMU ${osid} #${instanceid} copying hd.img...`;
			fs.copyFile(path.join(__dirname, "..", "qemu", osid, "hd.img"), path.join(instance.dirPath, "hd.img"), this);
		},
		function runQEMU()
		{
			const qemuArgs = ["-nodefaults", "-machine", "accel=kvm,dump-guest-core=off", "-rtc", "base=localtime", "-drive", "format=raw,if=ide,index=0,file=hd.img", "-boot", "order=c", "-vga", "cirrus"];
			if(!DEBUG)
				qemuArgs.push("-nographic");
			qemuArgs.push("-m", `size=${OS[osid].ram}`);
			if((OS[osid].cores || 1)>1)
				qemuArgs.push("-smp", `cores=${OS[osid].cores}`);
			qemuArgs.push("-netdev", `user,net=192.168.${OS[osid].subnet}.0/24,dhcpstart=${instance.ip},hostfwd=tcp:127.0.0.1:${instance.smbPort}-${instance.ip}:445,id=nd1`);
			qemuArgs.push("-device", "rtl8139,netdev=nd1");

			const qemuRunOptions = {silent : true, detached : true, cwd : instance.dirPath};
			if(DEBUG)
				qemuRunOptions.env = {DISPLAY : ":0"};

			instance.cp = runUtil.run(`qemu-system-${OS[osid].arch}`, qemuArgs, qemuRunOptions);
			instance.cp.on("exit", () => { instance.ready = false; instance.cp = null; XU.log`qemu ${osid} #${instanceid} has exited.`; });
			
			XU.log`QEMU ${osid} #${instanceid} launched, waiting for it to boot...`;

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
			XU.log`QEMU ${osid} #${instanceid} declared itself ready, mounting in/out...`;

			const mountArgs = ["-t", "cifs", "-o", `user=dexvert,pass=dexvert,port=${instance.smbPort},vers=1.0,sec=ntlm,gid=1000,uid=7777`];
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
	XU.log`QEMU ${body.osid} #${instance.instanceid} performing run request: ${body}`;

	const inDirPath = path.join(instance.dirPath, "in");
	const outDirPath = path.join(instance.dirPath, "out");
	const goAU3FilePath = path.join(inDirPath, "go.au3");
	const tmpGoAU3FilePath = fileUtil.generateTempFilePath(undefined, ".au3");

	function waitForGoAU3ToVanish(cb)
	{
		tiptoe(
			function checkExistance()
			{
				fileUtil.exists(goAU3FilePath, this);
			},
			function rescheduleIfNeeded(err, exists)
			{
				if(exists)
					setTimeout(() => waitForGoAU3ToVanish(cb), 100);
				else
					setImmediate(() => cb(err));
			}
		);
	}

	tiptoe(
		function copyInFiles()
		{
			// We use rsync here to handle both files and directories
			(body.inFilePaths || []).parallelForEach((inFilePath, subcb) => runUtil.run("rsync", ["-aL", inFilePath, path.join(inDirPath, "/")], runUtil.SILENT, subcb), this);
		},
		function writeAutoItScript()
		{
			// We write to a temp file first, and then copy it over in one go to prevent the supervisor.au3 from picking up an incomplete file
			fs.writeFile(tmpGoAU3FilePath, body.autoIt, XU.UTF8, this);
		},
		function moveAutoItScript()
		{
			fileUtil.move(tmpGoAU3FilePath, goAU3FilePath, this);
		},
		function waitForFinish()
		{
			waitForGoAU3ToVanish(this);
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
		function preClean()
		{
			XU.log`QEMU pre-cleaning ${INSTANCE_DIR_PATH}...`;
			fileUtil.unlink(INSTANCE_DIR_PATH, this);
		},
		function startOSInstances()
		{
			XU.log`QEMU starting instances...`;
			Object.keys(OS).parallelForEach((osid, subcb) => [].pushSequence(0, NUM_SERVERS-1).serialForEach((instanceid, instancecb) => startOS(osid, instanceid, instancecb), subcb), this);
		},
		function startCheckingQueue()
		{
			checkRunQueue();
			this();
		},
		cb
	);
};

// The QEMU supervisor.au3 script will call this when it's ready to go
exports.registerRoutes = function registerRoutes(fastify)
{
	fastify.get("/qemuReady", (request, reply) => readyOS(request.query.osid, Object.values(INSTANCES[request.query.osid]).find(v => v.ip===request.query.ip).instanceid, () => reply.send("ok")));
	fastify.post("/qemuRun", (request, reply) => { RUN_QUEUE.push({body : request.body, request, reply}); return undefined; });
};

// Return true if everything is ok
exports.status = function status()
{
	return Object.values(INSTANCES).flatMap(o => Object.values(o)).every(instance => instance.cp && instance.ready);
};

// Stops our unoconv background server
exports.stop = function stop(cb)
{
	function waitForNotReady(notreadycb)
	{
		if(Object.values(INSTANCES).flatMap(o => Object.values(o)).some(o => o.ready))
			setTimeout(() => waitForNotReady(notreadycb), 100);
		else
			setImmediate(notreadycb);
	}

	tiptoe(
		function killOSes()
		{
			Object.keys(OS).serialForEach((osid, subcb) => [].pushSequence(0, NUM_SERVERS-1).serialForEach((instanceid, instancecb) => stopOS(osid, instanceid, instancecb), subcb), this);
		},
		function waitForKilling()
		{
			waitForNotReady(this);
		},
		cb
	);
};
