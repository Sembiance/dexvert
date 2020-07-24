"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs"),
	path = require("path"),
	fileUtil = require("@sembiance/xutil").file,
	{DOS} = require("@sembiance/xutil").dos;

// Returns a function that when called will run DOSBox with the given autoExec
exports.run = function run({p, autoExec, bin, subdir, timeout=XU.MINUTE*3, screenshot, keys, keyOpts})
{
	return p.util.flow.serial([
		() => (subState, subP, cb) => ((bin || subdir) ? fs.symlink(path.join(__dirname, "..", "..", "dos", (bin || subdir)), path.join(subState.cwd, path.basename(bin || subdir)), cb) : setImmediate(cb)),
		() => (subState, subP, cb) =>
		{
			const quickOpArgs = {dosCWD : subState.cwd, autoExec, timeout, verbose : subState.verbose, tmpDirPath : subState.tmpDirPath, screenshot, keys, keyOpts};
			if(subState.verbose===5)
				quickOpArgs.video = fileUtil.generateTempFilePath(subState.tmpDirPath, ".mp4");
			return DOS.quickOp(quickOpArgs, cb);
		}
	]);
};
