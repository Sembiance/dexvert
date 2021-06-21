"use strict";
/* eslint-disable no-unused-vars */
const XU = require("@sembiance/xu"),
	path = require("path"),
	util = require("util"),
	tiptoe = require("tiptoe"),
	testUtil = require("../test/testUtil.js"),
	imageUtil = require("@sembiance/xutil").image,
	runUtil = require("@sembiance/xutil").run,
	fileUtil = require("@sembiance/xutil").file,
	{Iconv} = require("iconv"),
	fs = require("fs");


//runUtil.run("/usr/bin/ffprobe", ["-v", "0", "-select_streams", "v:0", "-count_frames", "-show_entries stream=nb_read_frames", "-of", "csv=p=0", "/mnt/ram/tmp/6695461950302124834461/turshow_001.avi"], {silent : true}, (...args) =>
runUtil.run("/usr/bin/ffprobe", ["-select_streams", "v:0", "-count_frames", "-show_entries stream=nb_read_frames", "/mnt/ram/tmp/6695461950302124834461/turshow_001.avi"], {silent : true}, (...args) =>
{
	XU.log`${args}`;
	process.exit(0);
});
