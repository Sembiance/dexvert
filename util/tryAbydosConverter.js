"use strict";
/* eslint-disable no-unused-vars */
const XU = require("@sembiance/xu"),
	path = require("path"),
	os = require("os"),
	util = require("util"),
	dexUtil = require("../src/dexUtil.js"),
	tiptoe = require("tiptoe"),
	testUtil = require("../test/testUtil.js"),
	runUtil = require("@sembiance/xutil").run,
	fileUtil = require("@sembiance/xutil").file,
	fs = require("fs");

const OUTDIRS = {};

tiptoe(
	function findSampleFiles()
	{
		testUtil.findSupportedSampleFilePaths(this.parallel());
		dexUtil.findFormats(this.parallel());
	},
	function performConverts(sampleFilePaths, dexFormats)
	{
		this.data.imageFormatEntries = Object.entries(dexFormats.image).filter(([, formatData]) => formatData.meta.mimeType && !formatData.meta.unsupported);
		XU.log`Found ${this.data.imageFormatEntries.length.toLocaleString()} supported abydosformats...`;
		this.data.imageFormatEntries.parallelForEach(([formatid, formatData], subcb) =>
		{
			OUTDIRS[formatid] = fileUtil.generateTempFilePath();
			fs.mkdirSync(OUTDIRS[formatid]);
			sampleFilePaths.filter(sampleFilePath => sampleFilePath.startsWith(`/mnt/compendium/DevLab/dexvert/test/sample/image/${formatid}/`)).parallelForEach((sampleFilePath, sfpcb) =>
			{
				runUtil.run("abydosconvert", ["--json", formatData.meta.mimeType, sampleFilePath, OUTDIRS[formatid]], {silent : true, timeout : XU.MINUTE}, sfpcb);
			}, subcb);
		}, this, os.cpus().length);
	},
	function checkOutputJSON(abydosFormatsResults)
	{
		this.data.imageFormatEntries.forEach(([formatid, formatData], i) =>
		{
			const abydosFormatResults = abydosFormatsResults[i].filter(abydosFormatResult => XU.parseJSON(abydosFormatResult, {}).width===0 && XU.parseJSON(abydosFormatResult, {}).height===0);
			if(abydosFormatResults.length>0)
				XU.log`${formatid}: ${abydosFormatResults}`;
		});
		this();
	},
	XU.FINISH
);

