"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "File Imploder",
	website : "http://fileformats.archiveteam.org/wiki/File_Imploder",
	ext     : [".imp"],
	magic   : ["File Imploder compressed data"],
	notes   : "Found some files that identified as IMP! but don't decompress with ancient. So don't currently have any file samples for this format."
};

exports.converterPriority = ["ancient"];
