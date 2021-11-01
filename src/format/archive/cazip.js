"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "CAZIP File",
	ext   : [".caz"],
	magic : ["CAZIP compressed file"]
};

exports.converterPriority = ["cazip"];
