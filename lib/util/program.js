"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	runUtil = require("@sembiance/xutil").run,
	fileUtil = require("@sembiance/xutil").file,
	tiptoe = require("tiptoe");

exports.runOptions = function runOptions(state)
{
	return {silent : state.verbose<=1, liveOutput : state.verbose>=5, timeout : XU.MINUTE*10, cwd : state.cwd};
};

// Runs the given lib/program/*
exports.run = function run(programRaw, options={})
{
	return (state, p, cb) =>
	{
		const program = typeof programRaw==="string" ? p.program[programRaw] : programRaw;
		
		if(state.id && state.id.brute && program.meta.bruteUnsafe)
			return setImmediate(cb);
		
		if(!state.run)
			state.run = {meta : {}, args : {}};
		
		if(options.stateFlags)
			Object.assign(state, options.stateFlags);

		const bin = (program.wine || program.bin)(state);

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
				const runArgs = options.args || (options.argsd ? program.args(state, p, ...options.argsd) : program.args(state, p));
				const runOptions = Object.assign(exports.runOptions(state), (options.runOptions || (program.runOptions ? program.runOptions(state, p) : {})));
				if(state.tmpDirPath)
					runOptions.tmpDirPath = state.tmpDirPath;

				if(runOptions.virtualX && state.verbose>=4 && !runOptions.recordVideoFilePath)
				{
					runOptions.recordVideoFilePath = fileUtil.generateTempFilePath(state.tmpDirPath, ".mp4");
					XU.log`Saving debug video to: ${runOptions.recordVideoFilePath}`;
				}

				if(runOptions.recordVideoFilePath)
					runOptions.videoProcessedCB = this.parallel();
				
				if(program.wine)
				{
					const wineOpts = {cmd : bin, args : runArgs};
					if(program.cwd)
						wineOpts.cwd = state.cwd;
					if(program.wineOptions)
						Object.assign(wineOpts, program.wineOptions(state, p));
					p.util.wine.run(wineOpts)(state, p, this.parallel());
				}
				else
				{
					runUtil.run(bin, runArgs, runOptions, this.parallel());
				}
			},
			function post(...results)
			{
				state.run[path.basename(bin)] = results;

				if(!program.post)
					return this();

				program.post(state, p, this);
			},
			function removeStateFlags()
			{
				if(options.stateFlags)
					Object.keys(options.stateFlags).forEach(stateFlag => { delete state[stateFlag]; });

				this();
			},
			cb
		);
	};
};
