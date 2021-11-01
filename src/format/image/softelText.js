"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Softel Teletext",
	ext      : [".ep1"],
	mimeType : "text/x-softel-teletext"
};

exports.converterPriority = ["abydosconvert"];
