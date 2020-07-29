"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "dBase/FoxBase/XBase Database File",
	website     : "http://fileformats.archiveteam.org/wiki/DBF",
	ext         : [".dbf"],
	magic       : [/(?:FoxBase\+?\/?)?dBase /, "dBASE Database"],
	bruteUnsafe : true
};

exports.preSteps = [state => { state.unoconvType = "csv"; }];
exports.steps = [() => ({program : "unoconv"})];
exports.postSteps = [state => { delete state.unoconvType; }];
