"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "EasyCalc Spreadsheet file",
	ext            : [".calc"],
	forbidExtMatch : true,
	magic          : ["EasyCalc spreadsheet"]
};

exports.converterPriority = ["strings"];
