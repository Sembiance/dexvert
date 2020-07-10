"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "BZip2 archive",
	ext     : [".bz2", ".bzip2"],
	magic   : ["bzip2 compressed data", "bzip2 compressed archive", "BZIP2 Compressed Archive"],
	program : "bunzip2"
};
