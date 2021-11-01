"use strict";
/* eslint-disable node/global-require */
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Ani ST",
	website        : "http://fileformats.archiveteam.org/wiki/AniST",
	ext            : [".scr", ".str"],
	mimeType       : "image/x-ani-st",
	forbiddenMagic : require("../executable/windowsSCR.js").meta.magic	// Never want to convert windows SCR files as an image
};

exports.converterPriority = ["abydosconvert"];
