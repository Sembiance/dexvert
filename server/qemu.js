"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	fs = require("fs"),
	tiptoe = require("tiptoe"),
	fileUtil = require("@sembiance/xutil").file,
	runUtil = require("@sembiance/xutil").run;

const OS =
{
	win2k : { arch : "i386", subnet : 50 }
};

const INSTANCES = {};
const NUM_SERVERS = 2;
const INSTANCE_DIR_PATH = "/mnt/ram/dexvert/qemu";
const RUN_QUEUE = [];

// Called to prepare the QEMU environment for a given OS and then start QEMU
function startOS(osid, instanceid, cb)
{
	if(!INSTANCES[osid])
		INSTANCES[osid] = {};
	
	const instance = {instanceid, dirPath : path.join(INSTANCE_DIR_PATH, instanceid.toString()), ready : false, busy : false};
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
			fs.copyFile(path.join(__dirname, "..", "qemu", osid, "hd.img"), path.join(instance.dirPath, "hd.img"), this);
		},
		function runQEMU()
		{
			const qemuArgs = ["-nodefaults", "-drive", "format=raw,if=ide,index=0,file=hd.img", "-boot", "order=c", "-vga", "cirrus", "-netdev"];
			qemuArgs.push(`user,net=192.168.${OS[osid].subnet}.0/24,dhcpstart=${instance.ip},hostfwd=tcp:127.0.0.1:${instance.smbPort}-${instance.ip}:445,id=nd1`);
			qemuArgs.push("-device", "rtl8139,netdev=nd1");

			instance.cp = runUtil.run(`qemu-system-${OS[osid].arch}`, qemuArgs, {silent : true, detached : true, cwd : instance.dirPath, env : {DISPLAY : ":0"}});
			instance.cp.on("exit", () => { instance.ready = false; instance.cp = null; XU.log`qemu ${osid} #${instanceid} has exited.`; });
			
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
			["in", "out"].serialForEach((v, subcb) => runUtil.run("sudo", ["umount", path.join(instance.dirPath, v)], runUtil.SILENT, subcb), this);
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

function performRun(instance, runData)
{
	XU.log`qemu performing run for request ${runData.body} on ${runData.body.osid} #${instance.instanceid}`;
	tiptoe(
		function copyInFiles()
		{
			// copy inFilePaths to instance.dirPath/in
			this();
		},
		function writeAutoItScript()
		{
			// We write to a temp file first, and then copy it over in one go to prevent the supervisor.au3 from picking up an incomplete file
			//fs.writeFile(fileUtil.generateTempPath, in/go.au3)
			this();
		},
		function moveAutoItScript()
		{
			//fileUtil.move(tmpGoAU3, in/go.au3
			this();
		},
		function waitForFinish()
		{
			//wait for the in/go.au3 script to disappear, deleted by the guest os supervisor
			this();
		},
		function copyResults()
		{
			// We use rsync here to preserve timestamps
			// TODO: Make sure the rsync command is going to preserve timestamps
			//runUtil.run(rsync, runData.outDirPath
			this();
		},
		function cleanFiles()
		{
			//runUtil.run(rm -rf *, cwd : path.join(instance.dirPath, "out")
			//runUtil.run(rm -rf *, cwd : path.join(instance.dirPath, "in")
			setTimeout(this, XU.SECOND*10);
		},
		function finishRun(err)
		{
			instance.busy = false;

			runData.reply.send(err ? `error ${err}` : "ok");
		}
	);
}

function checkRunQueue()
{
	if(RUN_QUEUE.length===0)
		return setTimeout(checkRunQueue, 100);
	
	const runData = RUN_QUEUE.shift();
	
	const instance = Object.values(INSTANCES[runData.body?.osid]).find(o => o.ready && !o.busy);
	if(!instance)
	{
		XU.log`qemu checkRunQueue failed to find an instance for ${runData.body}`;
		runData.reply.send("no instance available");
	}
	else
	{
		instance.busy = true;
		performRun(instance, runData);
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
			Object.keys(OS).serialForEach((osid, subcb) => [].pushSequence(0, NUM_SERVERS-1).serialForEach((instanceid, instancecb) => startOS(osid, instanceid, instancecb), subcb), this);
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
	return true;
};

// Stops our unoconv background server
exports.stop = function stop(cb)
{
	Object.keys(OS).serialForEach((osid, subcb) => [].pushSequence(0, NUM_SERVERS-1).serialForEach((instanceid, instancecb) => stopOS(osid, instanceid, instancecb), subcb), cb);
};
