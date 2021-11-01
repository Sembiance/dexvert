"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name : "Apple IIGS Preferred Format",
	ext  : [".gs", ".iigs", ".pnt", ".shr"],
	magic : ["Apple IIGS Preferred Format"]
};

exports.converterPriority = ["recoil2png"];
