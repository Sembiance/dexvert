"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	path = require("path"),
	fs = require("fs"),
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
exports.run = function run({cmd, args, cwd, delay=XU.SECOND*5, timeout=XU.MINUTE*2, autoItScript, preWineCleanup})
{
	return (state, p, cb) =>
	{
		const portNumFilePath = fileUtil.generateTempFilePath(state.tmpDirPath);
		const autoItScriptFilePath = fileUtil.generateTempFilePath(state.tmpDirPath, ".au3");
		const winePrefixDirPath = fileUtil.generateTempFilePath(state.tmpDirPath);

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
				if(state.tmpDirPath)
					runArgs.tmpDirPath = state.tmpDirPath;
				if(cwd)
					runArgs.cwd = cwd;
				if(state.verbose>=5)
				{
					runArgs.dontCropVideo = true;
					runArgs.recordVideoFilePath = fileUtil.generateTempFilePath(state.tmpDirPath, ".mp4");
					runArgs.videoProcessedCB = this.finish;
					XU.log`Saving debug video to: ${runArgs.recordVideoFilePath}`;
				}

				this.data.wineCP = runUtil.run("wine", [path.join(WINE_DIR_PATH, cmd), ...Array.force(args)], runArgs);

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
			function waitForProcess()
			{
				if(this.data.wineCP.exitCode===null)
					this.data.wineCP.on("exit", this);
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
			function waitForVideoProcessing()
			{
				if(state.verbose<5)
					return this();
				
				// Otherwise we are recording and we just do nothing as the videoProcessedCB will call finish when done. Hopefully.
			},
			cb
		);
	};
};
