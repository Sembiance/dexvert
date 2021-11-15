import {xu} from "xu";
import {fileUtil, runUtil} from "xutil";
import * as path from "https://deno.land/std@0.114.0/path/mod.ts";
import {delay} from "https://deno.land/std@0.114.0/async/mod.ts";
const DOS_SRC_PATH = path.join(xu.dirname(import.meta), "..", "dos");

export async function runDOS({cmd, args=[], root, autoExec, timeout=xu.MINUTE, screenshot, video, runIn, keys, keyOpts={}})
{
	const dosDirPath = (await fileUtil.exists(path.join(root, "dos")) ? (await fileUtil.genTempPath(root, "dos")) : path.join(root, "dos"));
	await Deno.mkdir(dosDirPath);

	await runUtil.run("rsync", ["-a", path.join(DOS_SRC_PATH, (cmd.includes("/") ? path.dirname(cmd) : cmd)), path.join(dosDirPath)]);
	await runUtil.run("rsync", ["-a", path.join(DOS_SRC_PATH, "c"), path.join(dosDirPath)]);

	const configFilePath = await fileUtil.genTempPath(root, ".conf");
	await Deno.copyFile(path.join(DOS_SRC_PATH, "dosbox.conf"), configFilePath);
	await fileUtil.searchReplace(configFilePath, "captures = capture", `captures = ${dosDirPath}`);

	const bootExecLines = [
		`mount C ${path.join(dosDirPath, "c")}`,
		"PATH C:\\DOS",
		"SET TEMP=C:\\TMP",
		"SET TMP=C:\\TMP",
		"C:\\CTMOUSE\\CTMOUSE /3",
		`mount E ${root}`,
		"E:",
		`COPY NUL ${path.basename(dosDirPath)}\\STARTED.UP`];
	
	function addBin(bin)
	{
		// if we want video or a screenshot and autoexec is not handling starting the video recording itself, then start video recording
		if((video || screenshot) && !(autoExec || []).includes("VIDREC.COM start"))
			bootExecLines.push("VIDREC.COM start");

		bootExecLines.push(...Array.force(autoExec || bin));

		// if we want video or a screenshot and autoexec isn't handling stopping the video recording itself, stop it here
		if((video || screenshot) && !(autoExec || []).includes("VIDREC.COM stop"))
			bootExecLines.push("VIDREC.COM stop");
	}

	if(runIn==="prog")
	{
		bootExecLines.push(`cd ${path.relative(root, path.join(dosDirPath, path.dirname(cmd))).replaceAll("/", "\\")}`);
		addBin(`${path.basename(cmd)} ${args.join(" ")}`);
	}
	else if(runIn==="out")
	{
		// TODO Add "out" support
	}
	else
	{
		addBin(`${path.basename(dosDirPath)}\\${cmd.replaceAll("/", "\\")} ${args.join(" ")}`);
	}
	
	// this will actualy cause dosbox to exit
	bootExecLines.push("REBOOT.COM");

	await fileUtil.writeFile(configFilePath, bootExecLines.join("\n"), "utf-8", {append : true});

	const runOptions = {detached : true, liveOutput : xu.verbose>=4, timeout};
	if(xu.verbose>=6)
		runOptions.env = {DISPLAY : ":0"};
	else
		runOptions.virtualX = true;

	const {p, xvfbPort} = await runUtil.run("dosbox", ["-conf", configFilePath], runOptions);
	let status = null;
	p.status().then(v => { status = v; });

	if(keys)
	{
		await xu.waitUntil(async () => !!(await fileUtil.exists(path.join(dosDirPath, "STARTED.UP"))), {timeout});
		await xu.waitUntil(() => !!status, {timeout : (keyOpts.delay || xu.SECOND*5)});
		
		for(const key of Array.force(keys))
		{
			if(status)
				break;
			
			if(Object.isObject(key) && key.delay)
			{
				await delay(key.delay);
				continue;
			}

			const xdotoolOptions = {verbose : xu.verbose>=5, liveOutput : xu.verbose>=5, timeout, env : {"DISPLAY" : `:${xvfbPort}`}};
			await runUtil.run("xdotool", ["search", "--class", "dosbox", "windowfocus", Array.isArray(key) ? "key" : "type", "--delay", "100", Array.isArray(key) ? key[0] : key], xdotoolOptions);

			if(keyOpts.interval)
				await delay(keyOpts.interval);
		}
	}

	await xu.waitUntil(() => !!status, {timeout});

	// TODO handle video/screenshot
	/*function findVideoIfNeeded()
		{
			if(!video && !screenshot)
				return this.jump(-2);
			
			fileUtil.glob(state.cwd, "*.avi", {nodir : true}, this);
		},
		function convertVideoOrGetFrameCount(videoFilePaths)
		{
			this.data.videoFilePath = videoFilePaths.multiSort([v => v]).last();

			if(screenshot)
				runUtil.run("ffprobe", ["-v", "0", "-select_streams", "v:0", "-count_frames", "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", this.data.videoFilePath], ffmpegRunOptions, this);
			else
				p.util.program.run("ffmpeg", {flags : {ffmpegExt : ".mp4"}, argsd : [this.data.videoFilePath, video]})(state, p, this);
		},
		function extractVideoFrame(frameCountRaw)
		{
			if(video)
				return this.jump(-2);
			
			runUtil.run("ffmpeg", ["-i", this.data.videoFilePath, "-filter_complex", `select='eq(n,${Math.round(screenshot.frameLoc.scale(0, 100, 0, (+frameCountRaw.trim())-1))})'`, "-vframes", "1", screenshot.filePath], ffmpegRunOptions, this);
		},*/
		
	return status;
}

/*class DOS
{
	// builder to get around the fact that constructors can't be async
	create({dosCWD, autoExec=[], tries=5, debug=false, recordVideo=false, timeout=xu.MINUTE*10}={})
	{
		const dos = new DOS();
		dos.dosCWD = dosCWD;
		dos.masterConfigFilePath = path.join(DOS_SRC_PATH, "dosbox.conf");
		dos.autoExec = autoExec;
		dos.dosBoxCP = null;
		dos.autoExecVanilla = null;
		dos.exitCallbacks = [];
		dos.timeout = timeout;
		dos.debug = debug;
		dos.tries = tries;
		dos.recordVideo = recordVideo;
		return dos;
	}

	// create a temporary directory in RAM and copy the master HD image and config file over
	async setup()
	{
		this.workDir = await fileUtil.genTempPath();
		this.configFilePath = path.join(this.workDir, path.basename(this.masterConfigFilePath));
		this.portNumFilePath = await fileUtil.genTempPath();

		await Deno.mkdir(this.workDir, {recursive : true});
		await Deno.copyFile(this.masterConfigFilePath, this.configFilePath);
		await fileUtil.searchReplace(this.configFilePath, "captures = capture", `captures = ${this.dosCWD}`);

		// addMountAndBootToConfig
		const bootExecLines = [
			`mount C ${C_DIR_PATH}`,
			"PATH C:\\DOS",
			"SET TEMP=C:\\TMP",
			"SET TMP=C:\\TMP",
			"C:\\CTMOUSE\\CTMOUSE /3",
			`mount E ${this.dosCWD}`,
			"E:"];
		if(this.recordVideo && !this.autoExec.includes("VIDREC start"))
			bootExecLines.push("VIDREC.COM start");
		bootExecLines.push(...this.autoExec);
		if(this.recordVideo && !this.autoExec.includes("VIDREC stop"))
			bootExecLines.push("VIDREC.COM stop");
		bootExecLines.push("REBOOT.COM");

		await fileUtil.writeFile(this.configFilePath, bootExecLines.join("\n"), "utf-8", {append : true});
	}

	// send the keys to the virtual doesbox window with the given delay then call the cb. Only works if virtualX was set
	sendKeys(keys, {interval=xu.SECOND, delay=xu.SECOND*10}={})
	{
		// TODO
		const {options, cb} = XU.optionscb(_options, _cb, {interval : XU.SECOND, delay : XU.SECOND*10});
	
		const self=this;
		setTimeout(() =>
		{
			if(!fileUtil.existsSync(self.portNumFilePath))
				return setImmediate(cb);

			const xPortNum = fs.readFileSync(self.portNumFilePath, XU.UTF8).trim();

			Array.force(keys).serialForEach((key, subcb) =>
			{
				if(Object.isObject(key) && key.delay)
					return setTimeout(subcb, key.delay), undefined;

				tiptoe(
					function sendKey()
					{
						const xdotoolOptions = {silent : self.verbose<=4, liveOutput : self.verbose>=5, env : {"DISPLAY" : `:${xPortNum}`}};
						runUtil.run("xdotool", ["search", "--class", "dosbox", "windowfocus", Array.isArray(key) ? "key" : "type", "--delay", "100", Array.isArray(key) ? key[0] : key], xdotoolOptions, this);
					},
					function waitDelay()
					{
						if(!options.interval)
							return this();

						setTimeout(this, options.interval);
					},
					subcb
				);
			}, cb);
		}, options.delay);
	}

	// Will start up DOSBox
	start(exitcb)
	{
		if(this.dosBoxCP!==null)
			throw new Error("DOSBox already running!");
		
		const runOptions = {detached : true};
		runOptions.liveOutput = xu.verbose>=4;
		runOptions.virtualX = !this.debug;
		runOptions.timeout = this.timeout;
		//TODO: runArgs.portNumFilePath = this.portNumFilePath;
			
		this.dosBoxCP = runUtil.run("dosbox", ["-conf", this.configFilePath], runOptions);
		

		//TODO this.dosboxOutput = new streamBuffers.WritableStreamBuffer();
		//TODO this.dosBoxCP.stdout.on("data", data => this.dosboxOutput.write(data));

		const r = await this.dosBoxCP.status();

		if(this.dosBoxCP.exitCode!==null)
			this.exitHandler();
		else
			this.dosBoxCP.once("exit", this.exitHandler.bind(this));

		if(exitcb)
			this.registerExitCallback(exitcb);
	}

	// Registers a cb to be called when DOSBox exits
	registerExitCallback(cb)
	{
		if(this.dosBoxCP===null)
			return setImmediate(cb);
			
		this.exitCallbacks.push(cb);
	}

	// Called when DOSBox exits
	exitHandler()
	{
		this.dosBoxCP = null;

		// Often DOSBox will fail to launch correctly. Either it'll just exit with no output, or an error about being unable to open X11 display. Not sure why. So let's uhm, just try again rofl
		const dosboxOutputString = this.dosboxOutput.getContentsAsString("utf8");
		if(!dosboxOutputString || dosboxOutputString.includes("Exit to error: Can't init SDL Couldn't open X11 display"))
		{
			if(this.verbose>=2)
				XU.log`DOSBox Failed to launch. ${this.tries>0 ? `Trying again with ${this.tries} remaining` : ""}`;

			if(this.tries>0)
			{
				this.tries-=1;
				this.start();
				return;
			}
		}

		this.exitCallbacks.splice(0, this.exitCallbacks.length).forEach(exitCallback => setImmediate(exitCallback));
	}

	// Will stop DOSBox
	stop(cb)
	{
		if(this.dosBoxCP===null)
			throw new Error("DOSBox not running!");
		
		this.exitCallbacks.push(cb);
		this.dosBoxCP.kill();
	}

	// Will remove any files created in workDir
	teardown(cb)
	{
		const self=this;
		tiptoe(
			function removeFiles()
			{
				if(self.verbose<5)
					fileUtil.unlink(self.workDir, this.parallel());
				fileUtil.unlink(self.portNumFilePath, this.parallel());
			},
			cb
		);
	}
}*/



	/*if(this.dosBoxCP!==null)
			throw new Error("DOSBox already running!");
		
		const runOptions = {detached : true};
		runOptions.liveOutput = xu.verbose>=4;
		runOptions.virtualX = !this.debug;
		runOptions.timeout = this.timeout;
		//TODO: runArgs.portNumFilePath = this.portNumFilePath;
			
		this.dosBoxCP = runUtil.run("dosbox", ["-conf", this.configFilePath], runOptions);
		

		//TODO this.dosboxOutput = new streamBuffers.WritableStreamBuffer();
		//TODO this.dosBoxCP.stdout.on("data", data => this.dosboxOutput.write(data));

		const r = await this.dosBoxCP.status();

		if(this.dosBoxCP.exitCode!==null)
			this.exitHandler();
		else
			this.dosBoxCP.once("exit", this.exitHandler.bind(this));

		if(exitcb)
			this.registerExitCallback(exitcb);*/

	/*

		// addMountAndBootToConfig
		

		await fileUtil.writeFile(this.configFilePath, bootExecLines.join("\n"), "utf-8", {append : true});*/

	//await Deno.remove(dosDirPath);

	/*const autoExecLines = autoExec || [`${path.basename(cmd)} ${args.join(" ")}`];
	const quickOpTmpDirPath = await fileUtil.genTempPath(undefined, "runDOS");
	const dosArgs = {dosCWD : cwd, autoExec : autoExecLines, debug : false};
	if(video || screenshot)
		dosArgs.recordVideo = true;
	if(timeout)
		dosArgs.timeout = timeout;
	
	
		function execCommands()
		{
			dos.start(this.parallel());
			if(keys)
				dos.sendKeys(Array.force(keys), keyOpts || {}, this.parallel());
		},
		function findVideoIfNeeded()
		{
			if(!video && !screenshot)
				return this.jump(-2);
			
			fileUtil.glob(state.cwd, "*.avi", {nodir : true}, this);
		},
		function convertVideoOrGetFrameCount(videoFilePaths)
		{
			this.data.videoFilePath = videoFilePaths.multiSort([v => v]).last();

			if(screenshot)
				runUtil.run("ffprobe", ["-v", "0", "-select_streams", "v:0", "-count_frames", "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", this.data.videoFilePath], ffmpegRunOptions, this);
			else
				p.util.program.run("ffmpeg", {flags : {ffmpegExt : ".mp4"}, argsd : [this.data.videoFilePath, video]})(state, p, this);
		},
		function extractVideoFrame(frameCountRaw)
		{
			if(video)
				return this.jump(-2);
			
			runUtil.run("ffmpeg", ["-i", this.data.videoFilePath, "-filter_complex", `select='eq(n,${Math.round(screenshot.frameLoc.scale(0, 100, 0, (+frameCountRaw.trim())-1))})'`, "-vframes", "1", screenshot.filePath], ffmpegRunOptions, this);
		},
		function teardown()
		{
			dos.teardown(this);
		},
		function cleanup()
		{
			if(state.verbose<5)
				fileUtil.unlink(quickOpTmpDirPath, this.parallel());
			this.parallel()();
		},
		cb
	);*/
