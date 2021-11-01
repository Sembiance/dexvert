"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Wireless Bitmap",
	website  : "http://fileformats.archiveteam.org/wiki/WBMP",
	ext      : [".wbmp", ".wap", "wbm"],
	mimeType : "image/vnd.wap.wbmp"
};

exports.converterPriority = ["convert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
