"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "ZX Spectrum Standard SCR",
	website             : "https://zxart.ee/eng/graphics/database/pictureType:standard/",
	ext                 : [".scr"],
	fileSize            : 6912,
	forbidFileSizeMatch : true,
	notes               : "Some files are originally animated (S.O.M. Tetris and lenn1st) but converters don't support this."
};

exports.converterPriorty = ["recoil2png", "convert", "nconvert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
