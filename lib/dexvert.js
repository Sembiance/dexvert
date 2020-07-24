"use strict";
/* eslint-disable node/global-require */
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	path = require("path"),
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
	cwd : process.cwd()
};

function init(cb)
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
		function findFormats(utilFilePaths, programFilePaths, familyFilePaths, formats)
		{
			const p =
			{
				util     : {},
				program  : {},
				families : {},
				C,
				DexvertError
			};

			[["util", utilFilePaths], ["program", programFilePaths], ["families", familyFilePaths]].forEach(([type, filePaths]) => filePaths.forEach(filePath => { p[type][path.basename(filePath, ".js")] = require(filePath); }));

			p.identify = require(path.join(__dirname, "identify.js"));
			p.process = require(path.join(__dirname, "process.js"));

			p.formats = formats;

			return p;
		},
		cb
	);
}

exports.identify = function identify(inputFilePath, _options, _cb)
{
	const {options, cb} = XU.optionscb(_options, _cb, {verbose : 0});

	const state = { ...baseState, verbose : options.verbose };
	dexUtil.setStateInput(state, inputFilePath);

	tiptoe(
		function performInit()
		{
			init(this);
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

exports.process = function process(inputFilePath, outputDirPath, {tmpDirPath=os.tmpdir(), verbose=0, brute=false, keepGoing=false, alwaysBrute=false}, cb)
{
	const state = { ...baseState, tmpDirPath, verbose };
	dexUtil.setStateInput(state, inputFilePath);
	dexUtil.setStateOutput(state, outputDirPath);

	if(state.verbose>=1)
		XU.log`Processing file: ${inputFilePath}\n`;

	tiptoe(
		function performInit()
		{
			init(this);
		},
		function performProcess(p)
		{
			if(state.verbose>=5)
				console.log(util.inspect(p.formats, {depth : Infinity, colors : true}));
				
			if(brute)
			{
				state.brute = brute==="all" ? C.FAMILIES : brute.split(",").map(v => v.trim()).filter(v => C.FAMILIES.includes(v));
				state.alwaysBrute = alwaysBrute;
			
				if(state.brute.length===0)
					delete state.brute;
			}

			if(state.brute && keepGoing)
				state.keepGoing = true;
			
			p.util.flow.serial(p.process.steps)(state, p, this);
		},
		function returnResults()
		{
			this(undefined, state);
		},
		cb
	);
};
