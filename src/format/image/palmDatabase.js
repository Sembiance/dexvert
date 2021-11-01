"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Palm Database ImageViewer format",
	website  : "http://fileformats.archiveteam.org/wiki/Palm_Database_ImageViewer",
	ext      : [".pdb"],
	magic    : ["Palm FireViewer bitmap", "FireViewer/ImageViewer PalmOS document", "Palm Pilot bitmap"]
};

exports.converterPriority = ["convert", "nconvert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
