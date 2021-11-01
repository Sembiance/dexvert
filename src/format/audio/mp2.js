"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "MPEG ADTS Layer II",
	ext            : [".mp2"],
	forbidExtMatch : true,
	magic          : ["MPEG ADTS, layer II"]
};

exports.converterPriority = ["ffmpeg"];
