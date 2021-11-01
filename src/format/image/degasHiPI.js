"use strict";
const XU = require("@sembiance/xu"),
	file = require("../../util/file.js");

exports.meta =
{
	name     : "Degas High Resolution Picture (PI)",
	website  : "http://fileformats.archiveteam.org/wiki/DEGAS_image",
	ext      : [".pi3", ".suh"],
	mimeType : "image/x-pi3",
	magic    : ["DEGAS hi-res bitmap"]
};

exports.idCheck = state => file.compareFileBytes(state.input.absolute, 0, Buffer.from([0x00, 0x02]));

// nconvert messes up with certain files such as vanna5.pi3
exports.converterPriority = ["recoil2png", "abydosconvert", "nconvert"];
