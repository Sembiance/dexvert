"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "MTV Ray-Tracer",
	website   : "http://fileformats.archiveteam.org/wiki/MTV_ray_tracer_bitmap",
	ext       : [".mtv", ".pic"],
	mimeType  : "image/x-mtv",
	magic     : ["zlib compressed data"],
	weakMagic : true
};

exports.converterPriorty = ["convert", "nconvert", "abydosconvert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
