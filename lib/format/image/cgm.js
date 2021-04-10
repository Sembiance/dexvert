"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Computer Graphics Metafile",
	website  : "http://fileformats.archiveteam.org/wiki/CGM",
	ext      : [".cgm"],
	mimeType : "image/cgm",
	magic    : ["Computer Graphics Metafile"],
	unsafe   : true,
	notes    : "Test file input.cgm fails to convert. I haven't located another CGM converter yet."
};

exports.converterPriorty = [{program : "unoconv", flags : {unoconvType : "svg"}}, "irfanView"];
