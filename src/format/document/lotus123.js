/*
import {Format} from "../../Format.js";

export class lotus123 extends Format
{
	name = "Lotus 1-2-3 File";
	website = "http://fileformats.archiveteam.org/wiki/Lotus_1-2-3";
	ext = [".wks",".wk1",".wk2",".wk3",".wk4",".123",".wkb"];
	magic = ["Lotus 123 Worksheet",{}];

steps = [null,null];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Lotus 1-2-3 File",
	website : "http://fileformats.archiveteam.org/wiki/Lotus_1-2-3",
	ext     : [".wks", ".wk1", ".wk2", ".wk3", ".wk4", ".123", ".wkb"],
	magic   : ["Lotus 123 Worksheet", /^Lotus 1-2-3 Wor[Kk][Ss]heet/],
};

// Several Lotus 123 docs back in the day were actually used for order forms and were meant to printed
// So we convert both to PDF and CSV
exports.steps =
[
	// PDF
	() => ({program : "soffice"}),

	// CSV
	() => ({program : "soffice", flags : {sofficeType : "csv"}})
];

*/
