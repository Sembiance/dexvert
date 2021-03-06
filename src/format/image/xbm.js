"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "X11 Bitmap",
	website  : "http://fileformats.archiveteam.org/wiki/XBM",
	ext      : [".xbm", ".bm"],
	mimeType : "image/x-xbitmap"
};

exports.converterPriorty = ["convert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
