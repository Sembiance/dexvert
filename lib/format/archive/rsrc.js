"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "MacOS Resource Fork",
	website : "http://fileformats.archiveteam.org/wiki/Macintosh_resource_file",
	ext     : [".rsrc"],
	magic   : ["Mac OSX datafork font", "AppleDouble Resource Fork", "AppleDouble encoded Macintosh file", "Mac AppleDouble encoded"],
	program : "deark"
};
