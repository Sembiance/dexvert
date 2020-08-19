"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "Computer Graphics Metafile",
	website     : "http://fileformats.archiveteam.org/wiki/CGM",
	ext         : [".cgm"],
	mimeType    : "image/cgm",
	magic       : ["Computer Graphics Metafile"],
	bruteUnsafe : true,
	notes       : "allprims.cgm and input.cgm both fail to convert. I haven't located another CGM converter yet."
};

exports.preSteps = [state => { state.unoconvType = "svg"; }];
exports.converterPriorty = ["unoconv"];
exports.converterExclude = ["*"];
exports.postSteps = [state => { delete state.unoconvType; }];
