"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	tiptoe = require("tiptoe"),
	fs = require("fs"),
	fileUtil = require("@sembiance/xutil").file,
	{DOS} = require("@sembiance/xutil").dos;

exports.run = function run({cmd, args=[], autoExec, timeout=XU.MINUTE, screenshot, video, includeDir, keys, keyOpts})
{
	return (state, p, cb) =>
	{
		const dosDirName = cmd.split("/")[0];

		tiptoe(
			function copyCMD()
			{
				// We copy the necessary DOS files to state.cwd in order to be able to run multiple instances of various apps at once, safely
				if(includeDir)
					fileUtil.copyDir(path.join(__dirname, "..", "..", "dos", dosDirName), path.join(state.cwd, dosDirName), this);
				else
					fs.copyFile(path.join(__dirname, "..", "..", "dos", cmd), path.join(state.cwd, path.basename(cmd)), this);
			},
			function prepare()
			{
				const autoExecLines = autoExec || [`${path.basename(cmd)} ${args.join(" ")}`];
				
				const quickOpArgs = {dosCWD : state.cwd, autoExec : autoExecLines, timeout, verbose : state.verbose, screenshot, video, keys, keyOpts};
				if(state.verbose>=5)
					quickOpArgs.video = fileUtil.generateTempFilePath(undefined, ".mp4");

				if(state.verbose>=3)
					XU.log`Running dosbox QuickOp with args ${quickOpArgs}`;

				DOS.quickOp(quickOpArgs, this);
			},
			cb
		);
	};
};
