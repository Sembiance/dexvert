"use strict";
const XU = require("@sembiance/xu"),
	file = require("../../util/file.js");

exports.meta =
{
	name    : "Mapletown Network",
	website  : "http://fileformats.archiveteam.org/wiki/Mapletown_Network",
	ext     : [".ml1", ".mx1", ".nl3"]
};

exports.idCheck = state =>
{
	const ext = state.input.ext.toLowerCase();
	if(ext===".ml1")
		return file.compareFileBytes(state.input.absolute, 0, Buffer.from([0x31, 0x30, 0x30, 0x1A]));
	if(ext===".mx1")
		return file.compareFileBytes(state.input.absolute, 0, Buffer.from([0x40, 0x40, 0x40, 0x20]));
	if(ext===".nl3")
		return file.compareFileBytes(state.input.absolute, 0, Buffer.from([0x20, 0x20, 0x78, 0x25]));
	
	return true;
};

exports.converterPriority = ["recoil2png"];
