"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Timeworks Publisher/Publish It!",
	ext            : [".dtp"],
	forbidExtMatch : true,
	magic          : ["Timeworks Publisher"],
	notes          : "All I could find on it: https://sparcie.wordpress.com/2018/01/22/open-access-for-dos/"
};

exports.converterPriorty = ["strings"];
