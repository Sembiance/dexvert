"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Excel Spreadsheet",
	website : "http://fileformats.archiveteam.org/wiki/XLS",
	ext     : [".xls"],
	magic   : ["Microsoft Excel worksheet", "Microsoft Excel for OS/2 worksheet", "Microsoft Excel sheet"]
};

exports.converterPriority = ["antixls"];
