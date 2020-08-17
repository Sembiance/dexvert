"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	fs = require("fs"),
	file = require(path.join(__dirname, "..", "..", "util", "file.js"));

exports.meta =
{
	name     : "Extended DEGAS Image",
	website  : "http://fileformats.archiveteam.org/wiki/Extended_DEGAS_image",
	ext      : [".pi4", ".pi5", ".pi6", ".pi7", ".pi8", ".pi9"],
	filesize : [state =>
	{
		const ext = state.input.ext.toLowerCase();
		if(ext===".pi4")
			return [77824, 154114];

		if(ext===".pi5")
			return 153634;

		if(ext===".pi7")
			return 308224;

		if(ext===".pi9")
			return [77824, 65024];

		if(exports.meta.ext.includes(ext))
			return fs.statSync(state.input.absolute).size;

		return undefined;
	}]
};

exports.idCheck = state =>
{
	const ext = state.input.ext.toLowerCase();
	if(ext===".pi5")
		return file.compareFileBytes(state.input.absolute, 0, Buffer.from([0x00, 0x04]));
	
	return true;
};

exports.converterPriorty = ["recoil2png"];
