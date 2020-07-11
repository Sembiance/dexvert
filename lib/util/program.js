"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	runUtil = require("@sembiance/xutil").run,
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
				const runArgs = options.args || program.args(state);
				const runOptions = Object.assign({silent : true, timeout : XU.MINUTE*10, cwd : state.cwd}, (options.runOptions || (program.runOptions ? program.runOptions(state) : {})));
				if(state.verbose>=4)
					runOptions.liveOutput = true;
				if(state.verbose>=2)
					XU.log`Running ${bin} in cwd ${state.cwd} with args ${runArgs} and options ${runOptions}`;

				runUtil.run(bin, runArgs, runOptions, this);
			},
			function post(...results)
			{
				if(!state.hasOwnProperty("run"))
					state.run = {};

				state.run[bin] = results;

				if(!program.post)
					return this();

				program.post(state, p, this);
			},
			cb
		);
	};
};
