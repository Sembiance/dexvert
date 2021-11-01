"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name             : "STOS Picture Packer",
	website          : "http://fileformats.archiveteam.org/wiki/Picture_Packer",
	ext              : [".pp1"],
	mimeType         : "image/x-stos-picturepacker-lowres",
	magic            : ["Picture Packer bitmap"]
};

exports.converterPriority = ["abydosconvert"];
