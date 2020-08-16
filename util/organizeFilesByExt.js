"use strict";
/* eslint-disable max-len, node/global-require */
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	path = require("path"),
	fs = require("fs"),
	tiptoe = require("tiptoe");

const DIR_PATH = "/mnt/compendium/DevLab/dexvert/sandbox/atari_graphics_studio_examples";

tiptoe(
	function findFiles()
	{
		fileUtil.glob(DIR_PATH, "*", {nodir : true}, this);
	},
	function createSubDirectories(filePaths)
	{
		this.data.filePaths = filePaths;
		filePaths.map(filePath => path.extname(filePath.toLowerCase())).unique().parallelForEach((ext, subcb) => fs.mkdir(path.join(DIR_PATH, ext.replaceAll(".", "")), subcb), this);
	},
	function moveFiles()
	{
		this.data.filePaths.parallelForEach((filePath, subcb) => fileUtil.move(filePath, path.join(DIR_PATH, path.extname(filePath.toLowerCase()).replaceAll(".", ""), path.basename(filePath)), subcb), this);
	},
	XU.FINISH
);
