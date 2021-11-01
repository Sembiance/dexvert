"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Hierarchical Data Format v5",
	website  : "http://fileformats.archiveteam.org/wiki/HDF",
	ext      : [".h5"],
	mimeType : "application/x-hdf",
	magic    : ["Hierarchical Data Format (version 5)", /^NCSA Hierarchical Data Format 5$/],
	notes    : "Only support converting to grayscale."
};

exports.converterPriority = ["h5topng"];
