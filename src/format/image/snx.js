"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Second Nature Screensaver Graphic",
	website : "http://fileformats.archiveteam.org/wiki/Second_Nature_Screensaver_Graphic",
	ext     : [".snx"],
	notes   : "This only is able to convert files that are just wrapped JPEG images (dragon*.snx). Others are in an unknown file format, including barw22.snx."
};

exports.converterPriority = ["irfanView", "foremost"];
