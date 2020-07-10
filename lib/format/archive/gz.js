"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "GZip archive",
	ext     : [".gz", ".gzip"],
	magic   : ["gzip compressed data", "GZipped data"],
	program : "gunzip"
};
