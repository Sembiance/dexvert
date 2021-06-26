"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	{performance} = require("perf_hooks"),
	runUtil = require("@sembiance/xutil").run,
	fileUtil = require("@sembiance/xutil").file,
	fs = require("fs"),
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

// Runs the given src/program/*
exports.run = function run(programRaw, options={})
{
	return (state, p, cb) =>
	{
		const program = typeof programRaw==="string" ? p.program[programRaw] : programRaw;
		
		if(state.id?.brute && program.meta.unsafe)
			return setImmediate(cb);
		
		// Don't run slow programs more than once
		if(program.meta.slow && state.ranPrograms.includes(program.meta.programid))
			return setImmediate(cb);
		
		if(!state.ran)
			state.ran = [];
		
		const r = {programid : program.meta.programid, counter : state.ran.length, meta : {}, flags : {}};
		if(state.id)
			r.id = XU.clone(state.id);
		if(options.flags)
		{
			const validFlags = Object.keys(program.meta.flags || {});
			const invalidFlags = Object.keys(options.flags).subtractAll(validFlags);
			if(invalidFlags.length>0)
			{
				console.trace();
				XU.log`\nInvalid flags ${invalidFlags} for program ${program.meta.programid}`;
				process.exit(0);
			}

			Object.assign(r.flags, options.flags);
		}
		
		state.ran.unshift(r);

		const bin = program.steps ? null : (program.qemu || program.dos || program.bin)(state);

		if(state.programFlags?.[bin])
			Object.assign(r.flags, state.programFlags[bin]);
		
		const prevCWDData = {};

		tiptoe(
			function changeCWD()
			{
				if(program.cwd)
				{
					prevCWDData.cwd = state.cwd;
					prevCWDData.inputFilePath = state.input.filePath;
					prevCWDData.outputDirPath = state.output.dirPath;

					const newCWD = program.cwd(state, p, r);
					state.cwd = newCWD.startsWith(path.sep) ? newCWD : path.join(state.cwd, newCWD);
					state.input.filePath = path.relative(state.cwd, path.join(prevCWDData.cwd, prevCWDData.inputFilePath));
					state.output.dirPath = path.relative(state.cwd, path.join(prevCWDData.cwd, prevCWDData.outputDirPath));
				}

				if(program.meta.symlinkUnsafe)
					fs.lstat(path.join(state.cwd, state.input.filePath), this);
				else
					this();
			},
			function resolveSymlink(inputSymlinkStat)
			{
				if(!program.meta.symlinkUnsafe || !inputSymlinkStat.isSymbolicLink())
					return this();
				
				fileUtil.unlinkSync(path.join(state.cwd, state.input.filePath));
				fs.copyFile(state.input.absolute, path.join(state.cwd, state.input.filePath), this);
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

				state.ranPrograms.pushUnique(r.programid);

				this.data.startedAt = performance.now();

				r.options = Object.assign(exports.runOptions(state), (options.runOptions || (program.runOptions ? program.runOptions(state, p, r) : {})));
				if(r.options["redirect-stdout"])
					process.exit(XU.log`${XU.cf.fg.red("WARNING")}: DO NOT SET runOptions redirect-stdout as it's buggy! Instead in the program set: ${"exports.redirectOutput"} for program ${r.programid}`);

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
				else
				{
					if(program.redirectOutput)
						runUtil.run(path.join(__dirname, "..", "..", "bin", "redirectOutput"), [program.redirectOutput(state), bin, ...r.args], r.options, runcb);
					else
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
			function revertState(err)
			{
				if(Object.keys(prevCWDData).length>0)
				{
					state.cwd = prevCWDData.cwd;
					state.input.filePath = prevCWDData.inputFilePath;
					state.output.dirPath = prevCWDData.outputDirPath;
				}

				cb(err);
			}
		);
	};
};
