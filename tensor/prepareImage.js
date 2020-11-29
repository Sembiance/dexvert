#!/usr/bin/env node
"use strict";
const XU = require("@sembiance/xu"),
	tensorUtil = require("./tensorUtil.js"),
	tiptoe = require("tiptoe");

tiptoe(
	function runClassification()
	{
		tensorUtil.prepareImage(process.argv[2], process.argv[3], this);
	},
	XU.FINISH
);
