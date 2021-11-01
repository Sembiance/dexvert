"use strict";
const XU = require("@sembiance/xu"),
	file = require("../../util/file.js");

exports.meta =
{
	name     : "Degas Low Resolution Picture (PI)",
	website  : "http://fileformats.archiveteam.org/wiki/DEGAS_image",
	ext      : [".pi1"],
	mimeType : "image/x-pi1"
};

exports.idCheck = state => file.compareFileBytes(state.input.absolute, 0, Buffer.from([0x00, 0x00]));

// abydosconvert hangs on KENSHIN.PI1
// nconvert fails to handle certain files properly such as alf23.pi1
exports.converterPriority = ["recoil2png", "abydosconvert", "nconvert"];
