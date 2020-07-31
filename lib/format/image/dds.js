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

exports.converterPriorty = ["nconvert", "convert"];
