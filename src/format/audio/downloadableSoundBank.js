"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Downloadable Sound Bank",
	website        : "https://en.wikipedia.org/wiki/DLS_format",
	ext            : [".dls"],
	forbidExtMatch : true,
	magic          : ["DownLoadable Sound bank"]
};

exports.converterPriority = ["awaveStudio"];
