"use strict";
/* eslint-disable node/global-require */
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	runUtil = require("@sembiance/xutil").run,
	httpUtil = require("@sembiance/xutil").http,
	printUtil = require("@sembiance/xutil").print,
	path = require("path"),
	fs = require("fs"),
	posix = require("posix"),
	{performance} = require("perf_hooks"),
	moment = require("moment"),
	util = require("util"),
	dexUtil = require("./dexUtil.js"),
	C = require("./C.js"),
	tiptoe = require("tiptoe");

class DexvertError extends Error
{
	constructor(state, ...params)
	{
		super(...params);

		this.name = "DexvertError";
		this.state = state;
	}
}

const baseState =
{
	cwd         : process.cwd(),
	ranPrograms : []
};

function init(state, cb)
{
	// Some programs produce core files, we don't want this.
	posix.setrlimit("core", {soft : 0});

	tiptoe(
		function getServerStatus()
		{
			if(state.op!=="process")
				return this();

			this.capture();
			httpUtil.get(`http://${C.DEXSERV_HOST}:${C.DEXSERV_PORT}/status`, this.parallel());
			httpUtil.get(`http://${C.TENSORSERV_HOST}:${C.TENSORSERV_PORT}/status`, this.parallel());
		},
		function findUtils(err, dexServResponse, tensorServerResponse)
		{
			if(state.op==="process" && (!dexServResponse || JSON.parse(dexServResponse[0]).status!==C.DEXSERV_OK_RESPONSE))
				throw new Error("dexserv not running!");
			
			if(state.op==="process" && (!tensorServerResponse || JSON.parse(tensorServerResponse[0]).status!==C.TENSORSERV_OK_RESPONSE))
				throw new Error("tensorServer not running!");

			fileUtil.glob(path.join(__dirname, "util"), "*.js", {nodir : true}, this.parallel());
			fileUtil.glob(path.join(__dirname, "program"), "**/*.js", {nodir : true}, this.parallel());
			fileUtil.glob(path.join(__dirname, "family"), "*.js", {nodir : true}, this.parallel());
			dexUtil.findFormats(this.parallel());
		},
		function findFiles(utilFilePaths, programFilePaths, familyFilePaths, formats)
		{
			const p =
			{
				util     : {},
				program  : {},
				families : {},
				C,
				DexvertError
			};

			[["util", utilFilePaths], ["program", programFilePaths], ["families", familyFilePaths]].forEach(([type, filePaths]) => filePaths.forEach(filePath =>
			{
				const o = require(filePath);
				const typeid = path.basename(filePath, ".js");
				p[type][typeid] = o;
				if(type==="program")
					o.meta.programid = typeid;
			}));

			p.identify = require("./identify.js");
			p.process = require("./process.js");

			p.formats = formats;

			return p;
		},
		cb
	);
}

exports.identify = function identify(_inputFilePath, _options, _cb)
{
	const inputFilePath = `${_inputFilePath}`;
	const {options, cb} = XU.optionscb(_options, _cb, {verbose : 0});

	const state = { ...baseState, op : "identify", verbose : options.verbose };
	dexUtil.setStateInput(state, inputFilePath);

	tiptoe(
		function performInit()
		{
			init(state, this);
		},
		function performIdentify(p)
		{
			p.util.flow.serial(p.identify.steps)(state, p, this);
		},
		function returnResults()
		{
			this(undefined, state.identify);
		},
		cb
	);
};

exports.process = function process(_inputFilePath, _outputDirPath, {verbose=0, brute=false, keepGoing=false, alwaysBrute=false, brutePrograms=false, useTmpOutputDir=null, transformed=false, dontTransform=false, asFormat, programFlags, ranPrograms=[]}, cb)
{
	const inputFilePath = `${_inputFilePath}`;
	const outputDirPath = `${_outputDirPath}`;

	const state = { ...baseState, op : "process", verbose, startedAt : performance.now() };
	let tmpOutputDirPath = null;
	if(asFormat)
		state.asFormat = asFormat;
	if(programFlags)
		state.programFlags = programFlags;
	if(ranPrograms)
		state.ranPrograms.pushUnique(...ranPrograms);
	if(transformed)
		state.transformed = true;
		
	dexUtil.setStateInput(state, inputFilePath);

	if(state.verbose>=1)
		XU.log`Processing file: ${inputFilePath}\n`;

	tiptoe(
		function checkOutputDir()
		{
			if(useTmpOutputDir)
				return this();

			fileUtil.glob(outputDirPath, "**", {nodir : true}, this);
		},
		function performInit(existingOutputFiles)
		{
			if(useTmpOutputDir || existingOutputFiles.length>0)
			{
				tmpOutputDirPath = fileUtil.generateTempFilePath(undefined, "");
				fs.mkdirSync(tmpOutputDirPath, {recursive : true});
			}

			dexUtil.setStateOutput(state, tmpOutputDirPath || outputDirPath);

			init(state, this);
		},
		function performProcess(p)
		{
			if(state.verbose>=6)
				console.log(util.inspect(p.formats, {depth : Infinity, colors : true}));
			
			if(brutePrograms)
			{
				state.brutePrograms = true;
				state.alwaysBrute = alwaysBrute;
			}

			if(brute)
			{
				state.brute = brute==="all" ? C.FAMILIES : brute.map(v => v.trim()).filter(v => C.FAMILIES.includes(v));
				state.alwaysBrute = alwaysBrute;
			
				if(state.brute.length===0)
					delete state.brute;
			}

			if((state.brute || state.brutePrograms) && keepGoing)
				state.keepGoing = true;

			p.util.flow.serial(p.process.steps)(state, p, this);
		},
		function moveFilesIfNecessary()
		{
			if(!tmpOutputDirPath)
				return this.jump(2);

			if(state.verbose>=1)
				XU.log`Moving files to output dir...`;
			runUtil.run("mv", ["--", ...(state.output.files || []).map(fp => (fp.includes(path.sep) ? fp.substring(0, fp.indexOf(path.sep)) : fp)).unique(), path.join(path.resolve(outputDirPath), "/")], {silent : true, cwd : tmpOutputDirPath}, this);
		},
		function cleanupTmpOutputDir()
		{
			if(state.verbose>=5)
				return this();

			if(state.verbose>=1)
				XU.log`Removing tmpOutputDirPath ${tmpOutputDirPath}`;
			fileUtil.unlink(tmpOutputDirPath, this);
		},
		function getOutputFileDates()
		{
			// This meta.ts is set if the input file has a date older than 2020. If it's not set, then we don't have a specific date for the input file, so don't set any dates on the output file
			if(!state.input.meta.ts)
				return this.jump(2);
			
			// It's possible for unzipped archives to include symlinks that point to files that don't exist which causes fs.stat to fail
			// So we eat any errors that fs.stat throws and the next function will remoev those files from the state.output.files list
			(state.output.files || []).parallelForEach((fp, subcb) => fs.stat(path.join(outputDirPath, fp), (err, statData) => subcb(undefined, err ? null : statData)), this);
		},
		function setOutputFileTimestamps(outputFilesStats)
		{
			const inputTS = moment(state.input.meta.ts, "YYYY-MM-DD").unix();
			(state.output.files || []).slice().parallelForEach((fp, subcb, i) =>
			{
				// If we don't have any stats, then fs.stat() failed which is critical enough to remove it from the state.output.files list
				if(!outputFilesStats[i])
				{
					if(state.verbose>=1)
						XU.log`ALERT! Removing output file ${fp} from the output.files list due to fs.stat having failed to run on it (possibly a broken symlink extracted from something?).`;
					state.output.files.removeAll(fp);
					return setImmediate(subcb);
				}

				// If our output file has a timestamp earlier than 2020 then it's assumed to be correct and shouldn't be overridden
				if(!outputFilesStats[i] || outputFilesStats[i].mtime.getFullYear()<2020)
					return setImmediate(subcb);

				// Otherwise we don't know the date. But we know it can't be any later than the input file date, so let's set the output file to the input file date
				fs.utimes(path.join(outputDirPath, fp), inputTS, inputTS, subcb);
			}, this);
		},
		function trimInputFile()
		{
			if(dontTransform || state.id)
				return this.finish();
			
			if(state.verbose>=1)
				printUtil.majorHeader("Transform: trimGarbage");
			
			processWithTransform("trimGarbage", outputDirPath, state, {verbose, brute, keepGoing, alwaysBrute, brutePrograms, useTmpOutputDir, asFormat, ranPrograms : state.ranPrograms}, this);
		},
		function stripInputFile(trimmedState)
		{
			if(trimmedState)
				return this.finish(undefined, trimmedState);

			if(state.verbose>=1)
				printUtil.majorHeader("Transform: stripGarbage");

			processWithTransform("stripGarbage", outputDirPath, state, {verbose, brute, keepGoing, alwaysBrute, brutePrograms, useTmpOutputDir, asFormat, ranPrograms : state.ranPrograms}, this.parallel());
		},
		function returnResult(err, r)
		{
			state.elapsedMS = performance.now()-state.startedAt;
			delete state.startedAt;
			
			cb(err, r || state);
		}
	);
};

function processWithTransform(transformType, outputDirPath, state, processOptions, cb)
{
	const transformedWorkDirPath = fileUtil.generateTempFilePath();
	const transformedFilePath = path.join(transformedWorkDirPath, state.input.base);
	let transformedState = undefined;

	tiptoe(
		function createWorkDir()
		{
			fs.mkdir(transformedWorkDirPath, {recursive : true}, this);
		},
		function performTransform()
		{
			runUtil.run(path.join(__dirname, "..", "transform", transformType, transformType), [state.input.absolute, transformedFilePath], runUtil.SILENT, this);
		},
		function checkExistance()
		{
			fileUtil.exists(transformedFilePath, this);
		},
		function performProcess(transformedFileExists)
		{
			if(!transformedFileExists)
				return this();
			
			exports.process(transformedFilePath, outputDirPath, {transformed : true, dontTransform : true, ...processOptions}, this);
		},
		function cleanup(stateResult)
		{
			if(stateResult?.ranPrograms)
				state.ranPrograms.pushUnique(...stateResult.ranPrograms);

			if(stateResult && stateResult.id && stateResult?.id?.formatid!=="emptyFile")	// eslint-disable-line @typescript-eslint/prefer-optional-chain
			{
				const transformedMeta = stateResult.input.meta;
				stateResult.input = XU.clone(state.input);
				stateResult.input.meta = transformedMeta;
				transformedState = stateResult;
			}

			if(state.verbose>=5)
				this();
			else
				fileUtil.unlink(transformedWorkDirPath, this);
		},
		function returnResult(err)
		{
			cb(err, transformedState);
		}
	);
}
