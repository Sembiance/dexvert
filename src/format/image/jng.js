"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "JPEG Network Graphics",
	website  : "http://fileformats.archiveteam.org/wiki/JNG",
	ext      : [".jng"],
	mimeType : "image/x-jng",
	magic    : ["JPEG Network Graphics", "JNG video data"]
};

exports.converterPriority = ["convert", "nconvert", "abydosconvert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
