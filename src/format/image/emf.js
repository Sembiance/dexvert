"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Microsoft Windows Enhanced Metafile",
	website  : "http://fileformats.archiveteam.org/wiki/EMF",
	ext      : [".emf"],
	mimeType : "image/emf",
	magic    : ["Windows Enhanced Metafile", "Microsoft Windows Enhanced Metafile"]
};

exports.converterPriority = ["deark", "convert", "abydosconvert", "irfanView"];
