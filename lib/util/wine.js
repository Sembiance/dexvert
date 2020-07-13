"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	path = require("path"),
	fs = require("fs"),
	fileUtil = require("@sembiance/xutil").file,
	runUtil = require("@sembiance/xutil").run;

const WINE_DIR_PATH = path.join(__dirname, "..", "..", "wine");

// AUTOIT DOCS: https://www.autoitscript.com/autoit3/docs/functions.htm

// Returns a function that when called will run wine with the given cmd and args and optional autoItScript
exports.run = function run({cmd, args, cwd, delay=XU.SECOND*5, timeout=XU.MINUTE*10, autoItScript})
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
				const runArgs = {detached : true, virtualX : true, silent : !state.verbose || state.verbose===0, verbose : state.verbose>=2, liveOutput : state.verbose>=4, virtualXPortNumFile : portNumFilePath, timeout, env : {WINEPREFIX : winePrefixDirPath}};
				if(cwd)
					runArgs.cwd = cwd;
				if(state.verbose>=5)
				{
					runArgs.recordVideoFilePath = fileUtil.generateTempFilePath(state.tmpDirPath, ".mp4");
					XU.log`Saving debug video to: ${runArgs.recordVirtualX}`;
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

				runUtil.run("wine", [path.join(WINE_DIR_PATH, "AutoIt3", "AutoIt3.exe"), autoItScriptFilePath], {silent : true, env : {"DISPLAY" : ":" + xPortNum, WINEPREFIX : winePrefixDirPath}}, this);
			},
			function waitForProcess()
			{
				if(this.data.wineCP.exitCode===null)
					this.data.wineCP.on("exit", this);
				else
					this();
			},
			function cleanup()
			{
				if(fileUtil.existsSync(autoItScriptFilePath))
					fileUtil.unlink(autoItScriptFilePath, this.parallel());

				fileUtil.unlink(portNumFilePath, this.parallel());
				fileUtil.unlink(winePrefixDirPath, this.parallel());
			},
			cb
		);
	};
};
