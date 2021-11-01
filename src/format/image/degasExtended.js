"use strict";
const XU = require("@sembiance/xu"),
	file = require("../../util/file.js");

exports.meta =
{
	name     : "Extended DEGAS Image",
	website  : "http://fileformats.archiveteam.org/wiki/Extended_DEGAS_image",
	ext      : [".pi4", ".pi5", ".pi6", ".pi7", ".pi8", ".pi9"],
	fileSize : {".pi4" : [77824, 154114], ".pi5" : 153634, ".pi7" : 308224, ".pi9" : [77824, 65024]}
};

exports.idCheck = state =>
{
	const ext = state.input.ext.toLowerCase();
	if(ext===".pi5")
		return file.compareFileBytes(state.input.absolute, 0, Buffer.from([0x00, 0x04]));
	
	return true;
};

exports.converterPriority = ["recoil2png"];
