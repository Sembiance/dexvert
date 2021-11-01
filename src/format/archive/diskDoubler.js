"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Disk Doubler",
	ext     : [".dd"],
	magic   : ["Disk Doubler compressed data"]
};

exports.converterPriority = ["unar"];
