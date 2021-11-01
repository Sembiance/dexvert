"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "DataBase Professional Database",
	ext            : [".db"],
	forbidExtMatch : true,
	magic          : ["DataBase Professional database"]
};

exports.converterPriority = ["strings"];
