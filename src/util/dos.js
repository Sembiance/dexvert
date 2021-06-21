"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	tiptoe = require("tiptoe"),
	fs = require("fs"),
	runUtil = require("@sembiance/xutil").run,
	fileUtil = require("@sembiance/xutil").file,
	streamBuffers = require("stream-buffers");

const DOS_DIR_PATH = path.join(__dirname, "..", "..", "dos");
const C_DIR_PATH = path.join(DOS_DIR_PATH, "c");

class DOS
{
	constructor({dosCWD, autoExec=[], tries=5, verbose=0, debug=false, recordVideo=false, timeout=XU.MINUTE*10}={})
	{
		this.dosCWD = dosCWD;
		this.masterConfigFilePath = path.join(DOS_DIR_PATH, "dosbox.conf");
		this.autoExec = autoExec;
		this.dosBoxCP = null;
		this.autoExecVanilla = null;
		this.exitCallbacks = [];
		this.timeout = timeout;
		this.debug = debug;
		this.tries = tries;
		this.verbose = verbose;
		this.recordVideo = recordVideo;
	}

	// Will create a temporary directory in RAM and copy the master HD image and config file over
	setup(cb)
	{
		this.workDir = fileUtil.generateTempFilePath();
		this.configFilePath = path.join(this.workDir, path.basename(this.masterConfigFilePath));
		this.portNumFilePath = fileUtil.generateTempFilePath();

		const self=this;
		tiptoe(
			function mkWorkDir()
			{
				fs.mkdir(self.workDir, {recursive : true}, this);
			},
			function copyConfig()
			{
				fs.copyFile(self.masterConfigFilePath, self.configFilePath, this);
			},
			function modifyConfigFile()
			{
				fileUtil.searchReplace(self.configFilePath, "captures = capture", `captures = ${self.dosCWD}`, this);
			},
			function addMountAndBootToConfig()
			{
				const bootExecLines = [
					`mount C ${C_DIR_PATH}`,
					"PATH C:\\DOS",
					"SET TEMP=C:\\TMP",
					"SET TMP=C:\\TMP",
					"C:\\CTMOUSE\\CTMOUSE /3",
					`mount E ${self.dosCWD}`,
					"E:"];
				if(self.recordVideo && !self.autoExec.includes("VIDREC start"))
					bootExecLines.push("VIDREC.COM start");
				bootExecLines.push(...self.autoExec);
				if(self.recordVideo && !self.autoExec.includes("VIDREC stop"))
					bootExecLines.push("VIDREC.COM stop");
				bootExecLines.push("REBOOT.COM");

				fs.appendFile(self.configFilePath, bootExecLines.join("\n"), XU.UTF8, this);
			},
			cb
		);
	}

	// Will send the keys to the virtual doesbox window with the given delay then call the cb. Only works if virtualX was set
	sendKeys(keys, _options, _cb)
	{
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
		
		const runArgs = {detached : true};
		runArgs.silent = this.verbose<=1 && !this.debug;
		runArgs.liveOutput = this.verbose>=3;
		runArgs.virtualX = !this.debug;
		runArgs.portNumFilePath = this.portNumFilePath;
		runArgs.timeout = this.timeout;
			
		this.dosBoxCP = runUtil.run("dosbox", ["-conf", this.configFilePath], runArgs, this);

		this.dosboxOutput = new streamBuffers.WritableStreamBuffer();
		this.dosBoxCP.stdout.on("data", data => this.dosboxOutput.write(data));

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
}

exports.run = function run({cmd, args=[], autoExec, timeout=XU.MINUTE, screenshot, video, includeDir, keys, keyOpts})
{
	return (state, p, cb) =>
	{
		const dosDirName = cmd.split("/")[0];
		const autoExecLines = autoExec || [`${path.basename(cmd)} ${args.join(" ")}`];
		const quickOpTmpDirPath = fileUtil.generateTempFilePath();
		const dosArgs = {dosCWD : state.cwd, autoExec : autoExecLines, verbose : state.verbose, debug : false};
		if(video || screenshot)
			dosArgs.recordVideo = true;
		if(timeout)
			dosArgs.timeout = timeout;
		
		const dos = new DOS(dosArgs);

		tiptoe(
			function copyCMD()
			{
				// We copy the necessary DOS files to state.cwd in order to be able to run multiple instances of various apps at once, safely
				if(includeDir)
					fileUtil.copyDir(path.join(DOS_DIR_PATH, dosDirName), path.join(state.cwd, dosDirName), this);
				else
					fs.copyFile(path.join(DOS_DIR_PATH, cmd), path.join(state.cwd, path.basename(cmd)), this);
			},
			function prepare()
			{
				fs.mkdir(quickOpTmpDirPath, {recursive : true}, this);
			},
			function setup()
			{
				dos.setup(this);
			},
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
					runUtil.run("ffprobe", ["-v", "0", "-select_streams", "v:0", "-count_frames", "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", this.data.videoFilePath], runUtil.SILENT, this);
				else
					p.util.program.run("ffmpeg", {flags : {ffmpegExt : ".mp4"}, argsd : [this.data.videoFilePath, video]})(state, p, this);
			},
			function extractVideoFrame(frameCountRaw)
			{
				if(video)
					return this.jump(-2);
				
				runUtil.run("ffmpeg", ["-i", this.data.videoFilePath, "-filter_complex", `select='eq(n,${Math.round(screenshot.frameLoc.scale(0, 100, 0, (+frameCountRaw.trim())-1))})'`, "-vframes", "1", screenshot.filePath], runUtil.SILENT, this);
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
		);
	};
};
//
