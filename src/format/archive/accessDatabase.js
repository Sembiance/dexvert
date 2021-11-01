"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "Microsoft Access Database",
	ext   : [".mdb"],
	magic : ["Microsoft Access Database", "Microsoft Jet DB"]
};

exports.converterPriority = ["unmdb"];
