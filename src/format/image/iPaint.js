"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "I Paint",
	ext   : [".ip"],
	magic : ["Ipaint bitmap"]
};

exports.converterPriority = ["recoil2png"];
