"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "SCR Package",
	ext            : [".spz"],
	forbidExtMatch : true,
	magic          : ["SCR Package"],
	notes          : "The format contains JPEG files, but I think it's done something to them as any extraction produces slightly corrupted results and just small images. Still, better than nothing."
};

exports.converterPriority = ["foremost"];
