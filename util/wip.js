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


runUtil.run("rsync", ["--verbose", "-aL", "-e", "ssh -i /mnt/compendium/DevLab/dexvert/qemu/gentoo/data/dexvert_id_rsa -o StrictHostKeyChecking=no -p 5320", "dexvert@127.0.0.1:/out/", "/mnt/ram/tmp/wip/"], {liveOutput : true}, (...args) =>
{
	XU.log`${args}`;
	process.exit(0);
});
