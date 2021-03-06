"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "Computer Graphics Metafile",
	website   : "http://fileformats.archiveteam.org/wiki/CGM",
	ext       : [".cgm"],
	mimeType  : "image/cgm",
	magic     : ["Computer Graphics Metafile"],
	weakMagic : true,
	notes     : "Test file input.cgm fails to convert"
};

exports.converterPriorty = [{program : "soffice", flags : {sofficeType : "svg"}}, "irfanView"];
