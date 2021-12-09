#!/usr/bin/env node
"use strict";
const XU = require("@sembiance/xu"),
	cmdUtil = require("@sembiance/xutil").cmd,
	cueParser = require("cue-parser");

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Attempts to parse <inputFilePath> as a CUE file",
	args :
	[
		{argid : "inputFilePath", desc : "File path to parse as a CUE file", required : true}
	]});

try
{
	console.log(JSON.stringify(cueParser.parse(argv.inputFilePath)));
}
catch(err)
{
	console.log(err);
}
