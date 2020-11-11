"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	dexUtil = require("../lib/dexUtil.js"),
	argv = require("minimist")(process.argv.slice(2), {boolean : true}),
	fileUtil = require("@sembiance/xutil").file,
	printUtil = require("@sembiance/xutil").print,
	tiptoe = require("tiptoe");

exports.DATA_DIR_PATH = path.join(__dirname, "data");
exports.SAMPLE_DIR_PATH = path.join(__dirname, "sample");

// Some files are just there for 'support' so we ignore them, or don't convert and take too long to try
const IGNORE_FILES =
{
	archive :
	{
		// Unsupported and can't reliably identify them
		corelThumbnails : "*"
	},
	audio :
	{
		// Unsupported and can't reliably identify them
		sonixSoundSample : "*"
	},
	image :
	{
		// Some FIG files will embed references to other images, such as pictures.fig, so we exclude these here
		fig : ["bugs.gif", "icebergs.jpg", "pumpkin.xbm", "teapot.xpm"]
	},
	font :
	{
		amigaBitmapFont : ["Diamonds.font"]
	}
};

exports.findSupportedSampleFilePaths = function findSupportedSampleFilePaths(cb)
{
	tiptoe(
		function findFormats()
		{
			dexUtil.findFormats(this);
		},
		function findSampleFiles(formats)
		{
			Object.forEach(formats, (family, familyFormats) => Object.forEach(familyFormats, formatid => fileUtil.glob(path.join(exports.SAMPLE_DIR_PATH, family, formatid), "*", {nodir : true}, this.parallel())));
		},
		function returnResults(...sampleFilePaths)
		{
			return sampleFilePaths.flat().filter(sampleFilePath =>
			{
				const [family, formatid, filename] = path.relative(exports.SAMPLE_DIR_PATH, sampleFilePath).split(path.sep);
				if(IGNORE_FILES[family] && IGNORE_FILES[family][formatid] && (IGNORE_FILES[family][formatid]==="*" || IGNORE_FILES[family][formatid].some(m => dexUtil.flexMatch(filename, m))))
					return false;

				return true;
			});
		},
		cb
	);
};

const logCounts = {};

exports.logResult = function logResult(status, sampleSubFilePath, msg="", ...args)
{
	if(!logCounts.hasOwnProperty(status))
		logCounts[status] = 0;

	logCounts[status] = logCounts[status] + 1;

	if(argv.verbose || status!=="PASS")
		XU.log`\n${XU.cf.fg.cyan("[")}${(status==="FAIL" ? XU.c.blink : "") + XU.c.fg[{FAIL : "red", SKIP : "yellow", PASS : "green"}[status]] + status}${XU.cf.fg.cyan("]")} ${XU.c.reset + XU.c.bold + sampleSubFilePath} ${XU.c.fg.orange + msg} ${args.length ? args : ""}`;	// eslint-disable-line max-len
	else
		process.stdout.write(".");

	return true;
};

exports.logFinish = function logFinish()
{
	printUtil.minorHeader("Test Results", {prefix : "\n"});
	Object.forEach(logCounts, (status, statusCount) => XU.log`${XU.cf.fg.cyan("[")}${(status==="FAIL" ? XU.c.blink : "") + XU.c.fg[{FAIL : "red", SKIP : "yellow", PASS : "green"}[status]] + status}${XU.cf.fg.cyan("]")} => ${statusCount.toLocaleString()}`);
};
