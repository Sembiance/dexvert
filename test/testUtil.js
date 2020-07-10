"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	dexUtil = require(path.join(__dirname, "..", "lib", "dexUtil.js")),
	fileUtil = require("@sembiance/xutil").file,
	tiptoe = require("tiptoe");

exports.DATA_DIR_PATH = path.join(__dirname, "data");
exports.SAMPLE_DIR_PATH = path.join(__dirname, "sample");

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
			return sampleFilePaths.flat();
		},
		cb
	);
};

exports.logResult = function logResult(status, sampleSubFilePath, msg="", ...args)
{
	XU.log`${XU.c.fg.cyan + "["}${(status==="FAIL" ? XU.c.blink : "") + XU.c.fg[{FAIL : "red", SKIP : "yellow", PASS : "green"}[status]] + status}${XU.c.fg.cyan + "]"} ${XU.c.reset + XU.c.bold + sampleSubFilePath} ${XU.c.fg.orange + msg} ${args.length ? args : ""}`;

	return true;
};
