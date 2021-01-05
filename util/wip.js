"use strict";
/* eslint-disable no-unused-vars */
const XU = require("@sembiance/xu"),
	path = require("path"),
	util = require("util"),
	tiptoe = require("tiptoe"),
	testUtil = require("../test/testUtil.js"),
	fileUtil = require("@sembiance/xutil").file,
	fs = require("fs");


process.exit(0);

tiptoe(
	function findSampleFiles()
	{
		testUtil.findSupportedSampleFilePaths(this);
	},
	function wip(sampleFilePaths)
	{
		const types = {};
		sampleFilePaths.forEach(sampleFilePath =>
		{
			const subFilePath = path.relative("/mnt/compendium/DevLab/dexvert/test/sample", sampleFilePath);
			const formatid = path.dirname(subFilePath);
			if(!types[formatid])
				types[formatid] = [];
			types[formatid].push(path.basename(subFilePath));
		});

		const haveEnough = [];
		Object.forEach(types, (formatid, filePaths) =>
		{
			if(filePaths.length>=3)
				haveEnough.push(formatid);
		});

		console.log(util.inspect(haveEnough, {depth : Infinity, maxArrayLength : Infinity}));

		this();
	},
	XU.FINISH
);

