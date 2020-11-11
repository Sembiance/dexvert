"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "ZX Spectrum Stellar",
	ext                 : [".stl"],
	fileSize            : 3072,
	forbidFileSizeMatch : true // recoil2png will convert any file, so we should only do it if we also have the proper extension
};

exports.converterPriorty = ["recoil2png"];
