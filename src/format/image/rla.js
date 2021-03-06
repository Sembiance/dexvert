"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Alias Wavefront RLA",
	website  : "http://fileformats.archiveteam.org/wiki/RLA",
	ext      : [".rla"],
	magic    : ["Alias Wavefront Raster bitmap"]
};

exports.converterPriorty = ["convert", "nconvert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
