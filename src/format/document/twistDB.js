"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Twist Database file",
	ext            : [".db"],
	forbidExtMatch : true,
	magic          : ["Twist DataBase"]
};

exports.converterPriority = ["strings"];
