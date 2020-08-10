"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	file = require(path.join(__dirname, "..", "..", "util", "file.js"));

exports.meta =
{
	name     : "Degas High Resolution Picture",
	website  : "http://fileformats.archiveteam.org/wiki/DEGAS_image",
	ext      : [".pc3"],
	mimeType : "image/x-pc3",
	magic    : ["DEGAS hi-res compressed bitmap"]
};

exports.custom = state => file.compareFileBytes(state.input.absolute, 0, 2, Buffer.from([0x80, 0x02]));

// nconvert fails to properly convert some files
exports.converterPriorty = ["recoil2png", "abydosconvert", "nconvert"];
