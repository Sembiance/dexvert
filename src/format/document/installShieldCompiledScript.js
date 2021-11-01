"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "InstallShield Compiled Script",
	ext   : [".inx"],
	magic : ["InstallShield Compiled Rules"]
};

exports.converterPriority = ["SID"];
