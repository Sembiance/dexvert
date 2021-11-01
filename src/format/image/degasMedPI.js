"use strict";
const XU = require("@sembiance/xu"),
	file = require("../../util/file.js");

exports.meta =
{
	name     : "Degas Medium Resolution Picture (PI)",
	website  : "http://fileformats.archiveteam.org/wiki/DEGAS_image",
	ext      : [".pi2"],
	mimeType : "image/x-pi2",
	magic    : ["DEGAS med-res bitmap"]
};

exports.idCheck = state => file.compareFileBytes(state.input.absolute, 0, Buffer.from([0x00, 0x01]));

// nconvert properly handles aspect ratio
exports.converterPriority = ["nconvert", "recoil2png"];
