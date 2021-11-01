"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "NEC PC-88 PI",
	ext   : [".pi"],
	magic : ["Pi bitmap"]
};

exports.converterPriority = ["recoil2png"];
