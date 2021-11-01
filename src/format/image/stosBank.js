"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "STOS Memory Bank",
	website  : "http://fileformats.archiveteam.org/wiki/STOS_memory_bank",
	ext      : [".mbk", ".mbs"],
	mimeType : "application/x-stos-memorybank",
	magic    : ["STOS Memory Bank", "STOS data"]
};

exports.converterPriority = ["abydosconvert"];
