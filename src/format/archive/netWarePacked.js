"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Novel NetWare Packed File",
	website : "http://fileformats.archiveteam.org/wiki/NetWare_Packed_File",
	magic   : ["Personal NetWare Packed File", "Novell Packed data"]
};

exports.converterPriority = ["nwunpack"];
