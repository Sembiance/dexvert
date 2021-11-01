"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Teletext Packets",
	ext      : [".t42"],
	mimeType : "text/x-t42-packets"
};

exports.converterPriority = ["abydosconvert"];
