"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "MS Compress Archive",
	ext     : ["_"],
	magic   : ["MS Compress archive data", "Microsoft SZDD compressed", "MS DOS Compression Format"],
	program : "msexpand"
};
