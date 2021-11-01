"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "Delphine CIN Video",
	ext         : [".cin"],
	magic       : ["Delphine CIN video"],
	unsupported : true,
	notes       : "FFMPEG has support for something called Delphine Software International CIN, but it couldn't convert the test files"
};
