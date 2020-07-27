"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "CorelDraw Document",
	website     : "http://fileformats.archiveteam.org/wiki/CorelDRAW",
	ext         : [".cdr", ".cdt", ".cdx", ".cpx"],
	magic       : ["CorelDraw Document", "CorelDraw Drawing"],
	bruteUnsafe : true
};

exports.preSteps = [state => { state.unoconvType = "svg"; }];
exports.converterPriorty = ["unoconv"];
exports.postSteps = [state => { delete state.unoconvType; }];
