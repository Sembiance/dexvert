"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Dune AAI Image",
	website  : "http://fileformats.archiveteam.org/wiki/AAI",
	ext      : [".aai"],
	mimeType : "image/x-dune"
};

exports.converterPriorty = ["convert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
