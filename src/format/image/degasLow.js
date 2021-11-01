"use strict";
const XU = require("@sembiance/xu"),
	file = require("../../util/file.js");

exports.meta =
{
	name     : "Degas Low Resolution Picture",
	website  : "http://fileformats.archiveteam.org/wiki/DEGAS_image",
	ext      : [".pc1"],
	mimeType : "image/x-pc1",
	magic    : ["DEGAS low-res compressed bitmap"]
};

exports.idCheck = state => file.compareFileBytes(state.input.absolute, 0, Buffer.from([0x80, 0x00]));

exports.converterPriority = ["recoil2png", "abydosconvert", "nconvert"];
