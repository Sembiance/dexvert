"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name     : "Dr. Halo",
	website  : "http://fileformats.archiveteam.org/wiki/Dr._Halo",
	ext      : [".cut", ".pal", ".pic"],
	priority : C.PRIORITY.LOW
};

exports.converterPriorty = ["convert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
