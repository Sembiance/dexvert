"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Atari RGB Intermediate",
	ext      : [".rgb"],
	mimeType : "image/x-atari-rgb-intermediate"
};

exports.converterPriorty = ["recoil2png", "abydosconvert"];
