"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	runUtil = require("@sembiance/xutil").run,
	tiptoe = require("tiptoe");

exports.run = function run(program, options={})
{
	return (state, p, cb) =>
	{
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
			function executeBin()
			{
				const runArgs = options.args || program.args(state);
				const runOptions = Object.assign({silent : true, cwd : state.cwd}, (options.runOptions || (program.runOptions ? program.runOptions(state) : {})));
				if(state.verbose>=2)
					XU.log`Running ${bin} in cwd ${state.cwd} with args ${runArgs} and options ${runOptions}`;
				if(state.verbose>=4)
					runOptions.liveOutput = true;

				runUtil.run(bin, runArgs, runOptions, this);
			},
			function stashResults(...results)
			{
				if(!state.hasOwnProperty("run"))
					state.run = {};

				state.run[bin] = results;

				this();
			},
			function runProgramPost()
			{
				if(!program.post)
					return this();
				
				program.post(state, p, this);
			},
			function runFormatPost()
			{
				if(!state.id)
					return this();

				const format = p.formats[state.id.family][state.id.formatid];
				if(!format.post)
					return this();
				
				format.post(state, p, this);
			},
			cb
		);
	};
};
