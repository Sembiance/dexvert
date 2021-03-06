"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "DirectDraw Surface",
	website  : "http://fileformats.archiveteam.org/wiki/DDS",
	ext      : [".dds"],
	mimeType : "image/x-direct-draw-surface",
	magic    : ["DirectX DirectDraw Surface", "Microsoft DirectDraw Surface", "DirectDraw Surface"]
};

// Both convert and nconvert sometimes produce an invalid image, but convert usually does better overall
exports.converterPriorty = ["convert", "nconvert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
