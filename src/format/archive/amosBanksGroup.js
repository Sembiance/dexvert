"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "AMOS Banks Group",
	ext      : [".abk"],
	magic    : ["AMOS Banks group", "AMOS Basic memory banks"]
};

exports.converterPriority = ["dumpamos"];
