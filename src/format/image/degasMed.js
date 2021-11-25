"use strict";
const XU = require("@sembiance/xu"),
	file = require("../../util/file.js");

exports.meta =
{
	name     : "Degas Medium Resolution Picture",
	website  : "http://fileformats.archiveteam.org/wiki/DEGAS_image",
	ext      : [".pc2"],
	mimeType : "image/x-pc2",
	magic    : ["DEGAS med-res compressed bitmap"]
};

exports.idCheck = state => file.compareFileBytes(state.input.absolute, 0, Buffer.from([0x80, 0x01]));

// nconvert properly handles aspect ratio
exports.converterPriority = ["nconvert", `abydosconvert[format:${this.mimeType}]`, "recoil2png"];
