"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "Graphic Workship Thumbnail",
	website             : "http://fileformats.archiveteam.org/wiki/Graphic_Workshop_Thumbnail",
	ext                 : [".thn"],
	magic               : ["Graphics Workshop for Windows Thumbnail"],
	fileSize            : 9480,
	forbidFileSizeMatch : true
};

exports.converterPriorty = [{ program : "deark", flags : {dearkModule : "gws_thn"} }];
