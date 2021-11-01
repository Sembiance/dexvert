"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "MRG Systems Teletext",
	ext      : [".tti"],
	mimeType : "text/x.teletext.tti"
};

exports.converterPriority = ["abydosconvert"];
