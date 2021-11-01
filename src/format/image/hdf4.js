"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Hierarchical Data Format v4",
	website  : "http://fileformats.archiveteam.org/wiki/HDF",
	ext      : [".hdf"],
	mimeType : "application/x-hdf",
	magic    : ["Hierarchical Data Format (version 4)", /^NCSA Hierarchical Data Format$/],
	notes    : "nconvert doesn't seem to handle all files, such as input_256 and input_truecolor"
};

exports.converterPriority = ["nconvert"];
