"use strict";
/* eslint-disable no-unused-vars */
const XU = require("@sembiance/xu"),
	path = require("path"),
	util = require("util"),
	tiptoe = require("tiptoe"),
	testUtil = require("../test/testUtil.js"),
	imageUtil = require("@sembiance/xutil").image,
	fileUtil = require("@sembiance/xutil").file,
	{Iconv} = require("iconv"),
	fs = require("fs");


const raw = fs.readFileSync("/home/sembiance/tmp/out/PMJPEG.txt");

const iconv = new Iconv("CP866", "UTF-8");
const out = iconv.convert(raw);

XU.log`${out.toString("UTF8")}`;
