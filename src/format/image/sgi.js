"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Silicon Graphics Image",
	website  : "http://fileformats.archiveteam.org/wiki/SGI_(image_file_format)",
	ext      : [".sgi", ".bw", ".rgba", ".rgb"],
	mimeType : "image/x-sgi",
	magic    : ["Silicon Graphics bitmap", "Silicon Graphics RGB bitmap", "SGI image data"]
};

exports.converterPriority = ["convert", "nconvert", "abydosconvert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
