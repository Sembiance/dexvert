"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Video Image Communication and Retrieval",
	website  : "http://fileformats.archiveteam.org/wiki/VICAR",
	ext      : [".vicar", ".vic", ".img"],
	mimeType : "image/x-vicar",
	magic    : ["VICAR JPL image bitmap", "PDS (VICAR) image data"]
};

exports.converterPriorty = ["convert", "abydosconvert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
