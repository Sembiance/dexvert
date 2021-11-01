"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name           : "iCEDraw Format",
	website        : "http://fileformats.archiveteam.org/wiki/ICEDraw",
	ext            : [".idf"],
	mimeType       : "image/x-icedraw",
	magic          : ["iCEDraw graphic"],
	forbiddenMagic : C.TEXT_MAGIC,
	unsafe    : true
};

exports.converterPriority = [{program : "ansilove", flags : {ansiloveType : "idf"}}, "abydosconvert"];
