"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	path = require("path"),
	fs = require("fs"),
	streamBuffers = require("stream-buffers"),
	fileUtil = require("@sembiance/xutil").file,
	runUtil = require("@sembiance/xutil").run;

const WINE_DIR_PATH = path.join(__dirname, "..", "..", "wine");

// AUTOIT DOCS: https://www.autoitscript.com/autoit3/docs/functions.htm
// Send() Keys: https://www.autoitscript.com/autoit3/docs/functions/Send.htm

exports.path = function winePath(unixPath)
{
	return `z:${unixPath.replaceAll("/", "\\")}`;
};

// Returns a function that when called will run wine with the given cmd and args and optional autoItScript
exports.run = function run({cmd, args, cwd, delay=XU.SECOND*5, timeout=XU.MINUTE*2, recordVideo, autoItScript, preWineCleanup})
{
	return (state, p, cb) =>
	{
		const portNumFilePath = fileUtil.generateTempFilePath();
		const autoItScriptFilePath = fileUtil.generateTempFilePath(undefined, ".au3");
		const winePrefixDirPath = fileUtil.generateTempFilePath();
		const wineOutput = new streamBuffers.WritableStreamBuffer();

		tiptoe(
			function createWinePrefixDir()
			{
				fs.mkdir(winePrefixDirPath, {recursive : true}, this);
			},
			function extractEnv()
			{
				runUtil.run("tar", ["-xf", path.join(WINE_DIR_PATH, "env.tar"), "-C", winePrefixDirPath], runUtil.SILENT, this);
			},
			function launchWine()
			{
				const runArgs = Object.assign(p.util.program.runOptions(state), {detached : true, virtualX : true, portNumFilePath, timeout, env : {WINEPREFIX : winePrefixDirPath}});
				if(cwd)
					runArgs.cwd = cwd;
				if(state.verbose>=5)
				{
					runArgs.dontCropVideo = true;
					runArgs.recordVideoFilePath = fileUtil.generateTempFilePath(undefined, ".mp4");
					runArgs.videoProcessedCB = this.finish;
					XU.log`Saving debug video to: ${runArgs.recordVideoFilePath}`;
				}

				if(recordVideo)
				{
					runArgs.recordVideoFilePath = recordVideo;
					runArgs.videoProcessedCB = this.finish;
				}

				this.data.wineCP = runUtil.run("wine", [path.join(WINE_DIR_PATH, cmd), ...Array.force(args)], runArgs);
				this.data.wineCP.stdout.on("data", d => wineOutput.write(d));
				this.data.wineCP.stderr.on("data", d => wineOutput.write(d));

				setTimeout(this, delay);
			},
			function executeAutoItScript()
			{
				if(!autoItScript)
					return this();
				
				fs.writeFileSync(autoItScriptFilePath, autoItScript, XU.UTF8);

				const xPortNum = fs.readFileSync(portNumFilePath, XU.UTF8).trim();

				runUtil.run("wine", [path.join(WINE_DIR_PATH, "AutoIt3", "AutoIt3.exe"), autoItScriptFilePath], {silent : true, env : {"DISPLAY" : `:${xPortNum}`, WINEPREFIX : winePrefixDirPath}}, this);
			},
			function waitForProcess(autoItResults)
			{
				if(autoItResults)
					wineOutput.write(autoItResults);

				if(this.data.wineCP.exitCode===null)
					this.data.wineCP.on("exit", () => this());	// exit cb passes (exitCode, signal) neither of which I really care about
				else
					this();
			},
			function performPreWineCleanup()
			{
				if(preWineCleanup)
					preWineCleanup(winePrefixDirPath, this);
				else
					this();
			},
			function cleanup()
			{
				if(fileUtil.existsSync(autoItScriptFilePath))
					fileUtil.unlink(autoItScriptFilePath, this.parallel());

				fileUtil.unlink(portNumFilePath, this.parallel());
				if(state.verbose<4)
					fileUtil.unlink(winePrefixDirPath, this.parallel());
			},
			function returnResults()
			{
				this(undefined, wineOutput.getContents().toString("utf8"));
			},
			cb
		);
	};
};
