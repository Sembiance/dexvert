#!/usr/bin/env node
"use strict";
const XU = require("@sembiance/xu"),
	tensorUtil = require("../tensorUtil.js"),
	tiptoe = require("tiptoe");

tiptoe(
	function runClassification()
	{
		tensorUtil.classifyImage(process.argv[2], "garbage", this);
	},
	function showResults(result)
	{
		console.log(result);

		this();
	},
	XU.FINISH
);
