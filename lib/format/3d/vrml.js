"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name             : "Virtual Reality Modeling Language",
	website          : "http://fileformats.archiveteam.org/wiki/VRML",
	ext              : [".wrl", ".wrz"],
	magic            : ["Virtual Reality Modeling Language", "ISO/IEC 14772 VRML 97 file"],
	unsupported      : true,
	unsupportedNotes : "A 3D rendering file format meant for the web. I didn't bother investigating it."
};
