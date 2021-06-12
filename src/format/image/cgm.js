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
	notes    : "Test file allprims.cgm and input.cgm fail to convert"
};

exports.converterPriorty = [{program : "soffice", flags : {sofficeType : "svg"}}, "irfanView"];
