"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Microsoft Windows Metafile",
	website  : "http://fileformats.archiveteam.org/wiki/WMF",
	ext      : [".wmf", ".apm", ".wmz"],
	mimeType : "image/wmf",
	magic    : [/^Windows [Mm]etafile/]
};

exports.converterPriorty = ["convert"];
