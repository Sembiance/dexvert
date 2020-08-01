"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs");

exports.meta =
{
	name     : "XGA",
	website  : "http://fileformats.archiveteam.org/wiki/XGA_(Falcon)",
	ext      : [".xga"],
	mimeType : "image/x-xga"
};

// XGA files are either 153600 or 368640 bytes long
exports.custom = state => ([153600, 368640].includes(fs.statSync(state.input.absolute).size));

exports.converterPriorty = ["recoil2png", "abydosconvert"];
