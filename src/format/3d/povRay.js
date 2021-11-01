"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name        : "POV-Ray Scene",
	website     : "http://fileformats.archiveteam.org/wiki/POV-Ray_scene_description",
	ext         : [".pov"],
	magic       : C.TEXT_MAGIC,
	weakMagic   : true,
	unsupported : true
};
