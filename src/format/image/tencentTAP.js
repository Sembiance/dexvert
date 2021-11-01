"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Tencent TAP",
	website  : "http://fileformats.archiveteam.org/wiki/TAP_(Tencent)",
	ext      : [".tap"],
	mimeType : "image/vnd.tencent.tap",
	magic    : ["TAP (Tencent) bitmap"]
};

exports.converterPriority = ["abydosconvert"];
