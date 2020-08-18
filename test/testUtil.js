"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	dexUtil = require(path.join(__dirname, "..", "lib", "dexUtil.js")),
	argv = require("minimist")(process.argv.slice(2), {boolean : true}),
	fileUtil = require("@sembiance/xutil").file,
	printUtil = require("@sembiance/xutil").print,
	tiptoe = require("tiptoe");

exports.DATA_DIR_PATH = path.join(__dirname, "data");
exports.SAMPLE_DIR_PATH = path.join(__dirname, "sample");

exports.findSupportedSampleFilePaths = function findSupportedSampleFilePaths(cb)
{
	tiptoe(
		function findFormats()
		{
			dexUtil.findFormats({verbose : 0}, this);
		},
		function findSampleFiles(formats)
		{
			Object.forEach(formats, (family, familyFormats) => Object.forEach(familyFormats, formatid => fileUtil.glob(path.join(exports.SAMPLE_DIR_PATH, family, formatid), "*", {nodir : true}, this.parallel())));
		},
		function returnResults(...sampleFilePaths)
		{
			return sampleFilePaths.flat();
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
