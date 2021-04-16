"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	{performance} = require("perf_hooks"),
	runUtil = require("@sembiance/xutil").run,
	fileUtil = require("@sembiance/xutil").file,
	tiptoe = require("tiptoe");

exports.runOptions = function runOptions(state)
{
	return {silent : state.verbose<=1, liveOutput : state.verbose>=5, timeout : XU.MINUTE*10, cwd : state.cwd};
};

exports.getRan = function getRan(state, programid)
{
	return state.ran.find(v => v.programid===programid);
};

exports.getMeta = function getMeta(state, programid)
{
	const meta = (exports.getRan(state, programid) || {meta : {}}).meta;
	return Object.keys(meta).length>0 ? meta : undefined;
};

exports.args = function args(state, p, programid)
{
	return p.program[programid].args(state, p, {flags : {}});
};

// Runs the given lib/program/*
exports.run = function run(programRaw, options={})
{
	return (state, p, cb) =>
	{
		const program = typeof programRaw==="string" ? p.program[programRaw] : programRaw;
		
		if(state.id?.brute && program.meta.unsafe)
			return setImmediate(cb);
		
		if(!state.ran)
			state.ran = [];
		
		const r = {programid : program.meta.programid, counter : state.ran.length, meta : {}, flags : {}};
		if(state.id)
			r.id = XU.clone(state.id);
		if(options.flags)
			Object.assign(r.flags, options.flags);
		
		state.ran.unshift(r);

		const bin = program.steps ? null : (program.qemu || program.dos || program.amiga || program.bin)(state);
		if(state.programFlags?.[bin])
			Object.assign(r.flags, state.programFlags[bin]);

		tiptoe(
			function changeCWD()
			{
				if(!program.cwd)
					return this();

				const prevInputFilePath = path.join(state.cwd, state.input.filePath);
				const prevOutputDirPath = path.join(state.cwd, state.output.dirPath);
				
				state.programPrevCWD = state.cwd;

				const newCWD = program.cwd(state, p, r);
				state.cwd = newCWD.startsWith(path.sep) ? newCWD : path.join(state.cwd, newCWD);
				state.input.filePath = path.relative(state.cwd, prevInputFilePath);
				state.output.dirPath = path.relative(state.cwd, prevOutputDirPath);

				this();
			},
			function preArgs()
			{
				if(!program.preArgs)
					return this();
				
				program.preArgs(state, p, r, this);
			},
			function generateArgsAndOptions()
			{
				r.args = options.args || (options.argsd ? program.args(state, p, r, ...options.argsd) : program.args(state, p, r));
				
				this();
			},
			function pre()
			{
				if(!program.pre)
					return this();

				program.pre(state, p, r, this);
			},
			function executeBin()
			{
				const runcb = this.parallel();

				this.data.startedAt = performance.now();

				r.options = Object.assign(exports.runOptions(state), (options.runOptions || (program.runOptions ? program.runOptions(state, p, r) : {})));

				if(program.steps)
				{
					p.util.flow.serial(program.steps(state, p, r))(state, p, runcb);
					return;
				}

				if(r.options.virtualX && state.verbose>=5 && !r.options.recordVideoFilePath)
				{
					r.options.recordVideoFilePath = fileUtil.generateTempFilePath(undefined, ".mp4");
					XU.log`Saving debug video to: ${r.options.recordVideoFilePath}`;
				}

				if(r.options.recordVideoFilePath)
					r.options.videoProcessedCB = this.parallel();
				
				if(program.qemu)
				{
					r.qemuData = {cmd : bin, args : r.args};
					if(program.qemuData)
						Object.assign(r.qemuData, program.qemuData(state, p, r));

					p.util.qemu.run(r.qemuData)(state, p, runcb);
				}
				else if(program.dos)
				{
					r.dosData = {cmd : bin, args : r.args};
					if(program.dosData)
						Object.assign(r.dosData, program.dosData(state, p, r));

					p.util.dos.run(r.dosData)(state, p, runcb);
				}
				else if(program.amiga)
				{
					r.amigaData = {cmd : bin, args : r.args};
					if(program.amigaData)
						Object.assign(r.amigaData, program.amigaData(state, p, r));

					p.util.amiga.run(r.amigaData)(state, p, runcb);
				}
				else
				{
					runUtil.run(bin, r.args, r.options, runcb);
				}
			},
			function post(results)
			{
				r.results = results;
				r.elapsedMS = performance.now()-this.data.startedAt;

				if(!program.post)
					return this();

				program.post(state, p, r, this);
			},
			cb
		);
	};
};
