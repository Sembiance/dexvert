"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	fileUtil = require("@sembiance/xutil").file,
	runUtil = require("@sembiance/xutil").run,
	{DOS} = require("@sembiance/xutil").dos;

// Returns a function that when called will run DOSBox with the given autoExec
exports.run = function run({state={}, p, autoExec, bin, subdir, timeout=XU.MINUTE*3, screenshot, video, keys, keyOpts})
{
	return p.util.flow.serial([
		// We used to symlink to bin||subdir, however this is problematic as if you are running multiple dosbox copies they might be shared file collisions during runtime
		() => (subState, subP, cb) => ((bin || subdir) ? runUtil.run("cp", ["-r", path.join(__dirname, "..", "..", "dos", (bin || subdir)), path.join(subState.cwd, path.basename(bin || subdir))], runUtil.SILENT, cb) : setImmediate(cb)),
		() => (subState, subP, cb) =>
		{
			const quickOpArgs = {dosCWD : subState.cwd, autoExec, timeout, verbose : subState.verbose, tmpDirPath : subState.tmpDirPath, screenshot, video, keys, keyOpts};
			if(state.verbose>=3)
				XU.log`Running dosbox QuickOp with args ${quickOpArgs}`;
				
			if(state.verbose===5)
				quickOpArgs.video = fileUtil.generateTempFilePath(state.tmpDirPath, ".mp4");
			return DOS.quickOp(quickOpArgs, cb);
		}
	]);
};
