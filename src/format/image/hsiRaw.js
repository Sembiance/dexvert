"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "HSI Raw",
	website : "http://fileformats.archiveteam.org/wiki/HSI_Raw",
	ext     : [".raw", ".hst"],
	magic   : ["HSI Raw bitmap"]
};

exports.converterPriorty = ["deark", "nconvert", "imageAlchemy"];
