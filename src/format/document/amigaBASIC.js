"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "AmigaBASIC Source Code",
	ext            : [".bas"],
	forbidExtMatch : true,
	magic          : ["AmigaBASIC source"],
	unsafe         : true
};

exports.converterPriorty = ["ab2ascii"];
