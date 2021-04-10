"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Lotus 1-2-3 File",
	website : "http://fileformats.archiveteam.org/wiki/Lotus_1-2-3",
	ext     : [".wks", ".wk1", ".wk2", ".wk3", ".wk4", ".123", ".wkb"],
	magic   : ["Lotus 123 Worksheet", /^Lotus 1-2-3 Wor[Kk][Ss]heet/],
	unsafe  : true
};

// Several Lotus 123 docs back in the day wer actually used for order formats and were meant to printed
// So we convert both to PDF and CSV
exports.steps =
[
	// PDF
	() => ({program : "unoconv"}),

	// CSV
	() => ({program : "unoconv", flags : {unoconvType : "csv"}})
];
