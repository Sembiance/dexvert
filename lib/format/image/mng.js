"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Multiple-image Network Graphics",
	website  : "http://fileformats.archiveteam.org/wiki/MNG",
	ext      : [".mng"],
	mimeType : "video/x-mng",
	magic    : ["Multiple-image Network Graphics bitmap", "MNG video data"]
};

exports.preSteps = [state => { state.convertExt = ".gif"; }];
exports.converterPriorty = ["convert"];
exports.postSteps = [state => { delete state.convertExt; }];
