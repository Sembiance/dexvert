"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Windows Clipboard",
	website : "http://fileformats.archiveteam.org/wiki/Windows_clipboard",
	ext     : [".clp"],
	magic   : ["Windows Clipboard"]
};

exports.converterPriorty = ["convert", "nconvert", "irfanView"];
