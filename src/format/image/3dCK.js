"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "3D Construction Kit",
	ext            : [".run"],
	forbidExtMatch : true,
	magic          : ["3D Construction Kit game Runner"],
	website        : "https://en.wikipedia.org/wiki/3D_Construction_Kit"
};

exports.converterPriority = ["runvga"];
