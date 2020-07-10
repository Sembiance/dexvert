"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "StoneCracker Archive",
	ext     : [".stc"],
	magic   : [/^StoneCracker .*compressed$/],
	program : "amigadepacker"
};
