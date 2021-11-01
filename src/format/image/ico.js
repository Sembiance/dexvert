"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Microsoft Windows Icon File",
	website  : "http://fileformats.archiveteam.org/wiki/ICO",
	ext      : [".ico"],
	magic    : ["Windows Icon", "MS Windows icon resource", "Icon File Format"]
};

// ICO file has multiple sub icons, which deark handles well. Fallback to nconvert
exports.converterPriority = ["deark", "nconvert"];
