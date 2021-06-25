"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "EDI Install LZS Compressed Data",
	ext            : ["$"],
	forbidExtMatch : true,
	magic          : ["EDI Install LZS compressed data"]
};

exports.converterPriorty = ["ediUnpack"];
