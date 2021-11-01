"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "StarWriter Document",
	ext   : [".tpl"],
	magic : ["StarWriter for MS-DOS document"],
	notes : "Soffice claims to support this format, but it wouldn't do anything with my .TPL files."
};

exports.converterPriority = ["strings"];
