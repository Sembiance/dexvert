"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name         : "Microsoft Compound Document",
	website      : "http://fileformats.archiveteam.org/wiki/Microsoft_Compound_File",
	magic        : ["Generic OLE2 / Multistream Compound", "Composite Document File V2 Document", "OLE2 Compound Document Format"],
	forbiddenExt : [".fpx"]	// Allow image/fpx to handle these
};

exports.steps = [() => ({program : "7z"})];
