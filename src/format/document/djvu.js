"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "DjVu Document",
	website  : "http://fileformats.archiveteam.org/wiki/DjVu",
	ext      : [".djvu", ".djv"],
	mimeType : "image/vnd.djvu",
	magic    : ["DjVu multi-page document", "DjVu File Format", "DjVu multiple page document"]
};

exports.converterPriority = ["ddjvu"];
