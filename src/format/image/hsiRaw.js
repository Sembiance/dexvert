"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "HSI Raw",
	website        : "http://fileformats.archiveteam.org/wiki/HSI_Raw",
	ext            : [".raw", ".hst"],
	forbidExtMatch : [".raw"],
	magic          : ["HSI Raw bitmap"]
};

exports.converterPriority = ["deark", "nconvert", "imageAlchemy"];
