#!/usr/bin/env node
"use strict";
const XU = require("@sembiance/xu"),
	tensorUtil = require("./tensorUtil.js"),
	runUtil = require("@sembiance/xutil").run,
	fileUtil = require("@sembiance/xutil").file,
	tiptoe = require("tiptoe");

const pngTrimmedPath = fileUtil.generateTempFilePath(undefined, ".png");
const RUN_OPTIONS = {silent : true};

tiptoe(
	function convertToPNG()
	{
		// We use [0] just in case the src image is an animation, so we just use the first frame
		runUtil.run("convert", [`${process.argv[2]}[0]`, pngTrimmedPath], RUN_OPTIONS, this);
	},
	function trimImage()
	{
		runUtil.run("autocrop", [pngTrimmedPath], RUN_OPTIONS, this);
	},
	function runClassification()
	{
		tensorUtil.prepareImage({inPath : pngTrimmedPath, outPath : process.argv[3], method : process.argv[4] || "centerCrop"}, this);
	},
	function cleanup()
	{
		fileUtil.unlink(pngTrimmedPath, this);
	},
	XU.FINISH
);
