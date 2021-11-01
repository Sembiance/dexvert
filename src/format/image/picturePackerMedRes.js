"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name             : "STOS Picture Packer",
	website          : "http://fileformats.archiveteam.org/wiki/Picture_Packer",
	ext              : [".pp2"],
	mimeType         : "image/x-stos-picturepacker-medres",
	magic            : ["Picture Packer bitmap"]
};

exports.converterPriority = ["abydosconvert"];
