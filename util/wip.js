"use strict";
/* eslint-disable no-unused-vars */
const XU = require("@sembiance/xu"),
	path = require("path"),
	util = require("util"),
	tiptoe = require("tiptoe"),
	testUtil = require("../test/testUtil.js"),
	imageUtil = require("@sembiance/xutil").image,
	fileUtil = require("@sembiance/xutil").file,
	fs = require("fs");

tiptoe(
	function getImageInfo()
	{
		imageUtil.getInfo("/home/sembiance/tmp/corvette.svg", {failFast : true}, this);
	},
	function wip(imgInfo)
	{
		XU.log`imgInfo ${imgInfo}`;

		this();
	},
	XU.FINISH
);

