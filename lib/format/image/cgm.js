"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Computer Graphics Metafile",
	website        : "http://fileformats.archiveteam.org/wiki/CGM",
	ext            : [".cgm"],
	forbidExtMatch : true,
	mimeType       : "image/cgm",
	magic          : ["Computer Graphics Metafile"],
	bruteUnsafe    : true
};

exports.preSteps = [state => { state.unoconvType = "svg"; }];
exports.converterPriorty = ["unoconv"];
exports.postSteps = [state => { delete state.unoconvType; }];
