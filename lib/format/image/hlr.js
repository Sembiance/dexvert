"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	file = require(path.join(__dirname, "..", "..", "util", "file.js"));

exports.meta =
{
	name     : "ZX Spectrum Attributes Gigascreen",
	ext      : [".hlr"],
	filesize : [1628]
};

exports.idCheck = state => file.compareFileBytes(state.input.absolute, 0, Buffer.from([0x76, 0xAF, 0xD3]));

exports.converterPriorty = ["recoil2png"];
