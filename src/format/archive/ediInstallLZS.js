"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "EDI Install LZS Compressed Data",
	ext            : ["$"],
	forbidExtMatch : true,
	magic          : ["EDI Install LZS compressed data", "EDI Install Pro LZSS2 compressed data"],
	notes          : "The EDI Install Pro sample file archives PA.HL$ and DWSPYDLL.DL$ do not unpack with the ediUnpack version I have. Haven't found a more recent version yet."
};

exports.converterPriority = ["ediUnpack"];
