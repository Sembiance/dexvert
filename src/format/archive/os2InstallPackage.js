"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "OS/2 Installation Package",
	ext         : [".pkg", ".pak"],
	magic       : ["OS/2 installation package/archive"],
	unsupported : true
};

//exports.converterPriority = ["os2Unpack"];
