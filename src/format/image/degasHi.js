"use strict";
const XU = require("@sembiance/xu"),
	file = require("../../util/file.js");

exports.meta =
{
	name     : "Degas High Resolution Picture",
	website  : "http://fileformats.archiveteam.org/wiki/DEGAS_image",
	ext      : [".pc3"],
	mimeType : "image/x-pc3",
	magic    : ["DEGAS hi-res compressed bitmap"]
};

exports.idCheck = state => file.compareFileBytes(state.input.absolute, 0, Buffer.from([0x80, 0x02]));

// nconvert fails to properly convert some files
exports.converterPriority = ["recoil2png", `abydosconvert[format:${this.mimeType}]`, "nconvert"];
