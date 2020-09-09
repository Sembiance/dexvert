"use strict";
/* eslint-disable max-len, node/global-require */
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	hashUtil = require("@sembiance/xutil").hash,
	path = require("path"),
	fs = require("fs"),
	tiptoe = require("tiptoe");

tiptoe(
	function findFiles()
	{
		fs.readFile(path.join(__dirname, "..", "test", "data", "identify.json"), XU.UTF8, this.parallel());
		fileUtil.glob(path.join(process.cwd()), "*", {nodir : true}, this.parallel());
	},
	function generateSums(identifyDataRaw, filePaths)
	{
		this.data.filePaths = filePaths;
		this.data.sampleFileSubpaths = Object.keys(JSON.parse(identifyDataRaw));
		
		Object.keys(JSON.parse(identifyDataRaw)).parallelForEach((sampleFilePath, subcb) => hashUtil.hashFile("sha1", path.join(__dirname, "..", "test", "sample", sampleFilePath), subcb), this.parallel());
		filePaths.parallelForEach((filePath, subcb) => hashUtil.hashFile("sha1", filePath, subcb), this.parallel());
	},
	function checkForExistingSums(existingSums, newSums)
	{
		newSums.forEach((newSum, i) => XU.log`${XU.cf.fg.white(path.basename(this.data.filePaths[i]))}: ${existingSums.includes(newSum) ? XU.cf.fg.red("ALREADY EXISTS") : XU.cf.fg.green("new file")}`);
	},
	XU.FINISH
);
