"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Portable Compiled Format",
	website : "http://fileformats.archiveteam.org/wiki/PCF",
	ext     : [".pcf"],
	magic   : ["X11 Portable Compiled Font data"]
};

exports.steps = [() => ({program : "deark"})];
exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
