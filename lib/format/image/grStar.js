"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs");

exports.meta =
{
	name     : "Graphics 7/8/9/9+/10/11 Image",
	website  : "http://fileformats.archiveteam.org/wiki/GR*",
	ext      : [".gr7", ".gr8", ".gr9", ".gr9p", ".g10", ".g11"],
	filesize : [state =>
	{
		const ext = state.input.ext.toLowerCase();
		if([".gr8", ".gr9"].includes(ext))
			return [7680, 7682, 7684];

		if(ext===".g10")
			return 7689;
		
		if(exports.meta.ext.includes(ext))
			return fs.statSync(state.input.absolute).size;

		return undefined;
	}]
};

exports.converterPriorty = ["recoil2png"];
