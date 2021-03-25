"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Joint Bi-Level Image experts Group",
	website  : "http://fileformats.archiveteam.org/wiki/JBIG",
	ext      : [".jbg", ".jbig", ".bie"],
	magic    : ["JBIG raster bitmap"],
	notes    : "Sample file mx.jbg converts to garbage, not sure why. reaConverter produces the same output."
};

exports.converterPriorty = ["convert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
