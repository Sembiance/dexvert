"use strict";
/* eslint-disable  prefer-named-capture-group */
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Unix Archive - Old",
	unsupported    : true,
	ext            : [".a"],
	forbidExtMatch : true,
	magic          : [/old (16|32)-bit-int (little|big)-endian archive/],
	weakMagic      : true
};
