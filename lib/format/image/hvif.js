"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Haiku Vector Icon Format",
	website  : "http://fileformats.archiveteam.org/wiki/Haiku_Vector_Icon_Format",
	ext      : [".hvif"],
	mimeType : "image/x-hvif",
	magic    : ["Haiku Vector Icon Format"],
	notes    : XU.trim`
		Several HVIF files don't appear to convert correctly with abydosconvert.
		I located an hvif2svg haskell program but it's even worse.
		So for now these particular HVIF files just won't be supported.`
};

exports.converterPriorty = ["abydosconvert"];
