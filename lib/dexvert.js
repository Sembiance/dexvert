"use strict";
/* eslint-disable node/global-require */
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	runUtil = require("@sembiance/xutil").run,
	path = require("path"),
	fs = require("fs"),
	posix = require("posix"),
	util = require("util"),
	os = require("os"),
	dexUtil = require(path.join(__dirname, "dexUtil.js")),
	C = require(path.join(__dirname, "C.js")),
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
	cwd  : process.cwd()
};

function init(state, cb)
{
	// Some programs produce core files, we don't want this.
	posix.setrlimit("core", {soft : 0});

	tiptoe(
		function findUtils()
		{
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
				p[type][path.basename(filePath, ".js")] = o;
			}));

			p.identify = require(path.join(__dirname, "identify.js"));
			p.process = require(path.join(__dirname, "process.js"));

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

	const state = { ...baseState, verbose : options.verbose };
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

exports.process = function process(_inputFilePath, _outputDirPath, {tmpDirPath=os.tmpdir(), verbose=0, brute=false, keepGoing=false, alwaysBrute=false, brutePrograms=false, midiFont=null}, cb)
{
	const inputFilePath = `${_inputFilePath}`;
	const outputDirPath = `${_outputDirPath}`;

	const state = { ...baseState, tmpDirPath, verbose };
	let tmpOutputDirPath = null;
	if(midiFont)
		state.midiInstrument = midiFont;
	dexUtil.setStateInput(state, inputFilePath);

	if(state.verbose>=1)
		XU.log`Processing file: ${inputFilePath}\n`;

	tiptoe(
		function checkOutputDir()
		{
			fileUtil.glob(outputDirPath, "**", {nodir : true}, this);
		},
		function performInit(existingOutputFiles)
		{
			if(existingOutputFiles.length>0)
			{
				tmpOutputDirPath = fileUtil.generateTempFilePath(tmpDirPath, "");
				fs.mkdirSync(tmpOutputDirPath, {recursive : true});
			}

			dexUtil.setStateOutput(state, tmpOutputDirPath || outputDirPath);

			init(state, this);
		},
		function performProcess(p)
		{
			if(state.verbose>=5)
				console.log(util.inspect(p.formats, {depth : Infinity, colors : true}));
			
			if(brutePrograms)
			{
				state.brutePrograms = true;
				state.alwaysBrute = alwaysBrute;
			}

			if(brute)
			{
				state.brute = brute==="all" ? C.FAMILIES : brute.split(",").map(v => v.trim()).filter(v => C.FAMILIES.includes(v));
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
				return this();

			if(state.verbose>=1)
				XU.log`Moving files to output dir...`;
			runUtil.run("mv", ["--", ...(state.output.files || []).map(fp => (fp.includes(path.sep) ? fp.substring(0, fp.indexOf(path.sep)) : fp)).unique(), path.join(path.resolve(outputDirPath), "/")], {silent : true, cwd : tmpOutputDirPath}, this);
		},
		function returnResults()
		{
			this(undefined, state);
		},
		cb
	);
};
