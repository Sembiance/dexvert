"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Matlab MAT",
	website  : "http://fileformats.archiveteam.org/wiki/MAT",
	ext      : [".mat"],
	mimeType : "application/x-matlab-data",
	magic    : ["Matlab Level 5 MAT-File", "Matlab v5 mat-file"],
	notes    : "I believe a .mat file can contain more than images, but right now we only support converting images."

};

exports.converterPriority = ["convert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
