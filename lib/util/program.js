"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	runUtil = require("@sembiance/xutil").run,
	fileUtil = require("@sembiance/xutil").file,
	tiptoe = require("tiptoe");

// Runs the given lib/program/*
exports.run = function run(program, options={})
{
	return (state, p, cb) =>
	{
		if(state.id && state.id.brute && program.meta.bruteUnsafe)
			return setImmediate(cb);

		const bin = program.bin(state);

		tiptoe(
			function changeCWD()
			{
				if(!program.cwd)
					return this();

				const prevInputFilePath = path.join(state.cwd, state.input.filePath);
				const prevOutputDirPath = path.join(state.cwd, state.output.dirPath);
				
				state.programPrevCWD = state.cwd;

				const newCWD = program.cwd(state);
				if(newCWD.startsWith(path.sep))
					state.cwd = newCWD;
				else
					state.cwd = path.join(state.cwd, newCWD);

				state.input.filePath = path.relative(state.cwd, prevInputFilePath);
				state.output.dirPath = path.relative(state.cwd, prevOutputDirPath);

				this();
			},
			function pre()
			{
				if(!program.pre)
					return this();

				program.pre(state, p, this);
			},
			function executeBin()
			{
				const runArgs = options.args || program.args(state, p);
				const runOptions = Object.assign({silent : state.verbose<=1, liveOutput : state.verbose>=5, timeout : XU.MINUTE*10, cwd : state.cwd}, (options.runOptions || (program.runOptions ? program.runOptions(state, p) : {})));
				if(state.tmpDirPath)
					runOptions.tmpDirPath = state.tmpDirPath;

				if(runOptions.virtualX && state.verbose>=4 && !runOptions.recordVideoFilePath)
				{
					runOptions.recordVideoFilePath = fileUtil.generateTempFilePath(state.tmpDirPath, ".mp4");
					XU.log`Saving debug video to: ${runOptions.recordVideoFilePath}`;
				}

				if(runOptions.recordVideoFilePath)
					runOptions.videoProcessedCB = this.parallel();
					
				runUtil.run(bin, runArgs, runOptions, this.parallel());
			},
			function post(...results)
			{
				if(!state.hasOwnProperty("run"))
					state.run = {};

				state.run[path.basename(bin)] = results;

				if(!program.post)
					return this();

				program.post(state, p, this);
			},
			cb
		);
	};
};
