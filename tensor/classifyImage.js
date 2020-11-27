"use strict";
const XU = require("@sembiance/xu"),
	httpUtil = require("@sembiance/xutil").http,
	C = require("../lib/C.js"),
	tiptoe = require("tiptoe");

tiptoe(
	function runTensorFlow()
	{
		httpUtil.post(`http://127.0.0.1:${C.TENSORSERV_PORT}/classify/garbage`, {imagePath : process.argv[2]}, {postAsJSON : true}, this);
	},
	function showResults(result)
	{
		console.log(result.toString());
		this();
	},
	XU.FINISH
);
