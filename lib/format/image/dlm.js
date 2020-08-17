"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs");

exports.meta =
{
	name     : "Dir Logo Maker",
	website  : "http://fileformats.archiveteam.org/wiki/Dir_Logo_Maker",
	ext      : [".dlm"],
	filesize : [256]
};

exports.idCheck = state => (fs.readFileSync(state.input.absolute)[0]==="B".charCodeAt(0));

exports.converterPriorty = ["recoil2png"];
