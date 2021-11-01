"use strict";
const XU = require("@sembiance/xu"),
	file = require("../../util/file.js");

exports.meta =
{
	name : "TRS-80",
	ext  : [".grf", ".max", ".p41", ".pix"]
};

exports.idCheck = state => file.compareFileBytes(state.input.absolute, 0, Buffer.from([0x00, 0x18]));

exports.converterPriority = ["recoil2png"];
