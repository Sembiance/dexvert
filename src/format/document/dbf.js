/*
import {Format} from "../../Format.js";

export class dbf extends Format
{
	name = "dBase/FoxBase/XBase Database File";
	website = "http://fileformats.archiveteam.org/wiki/DBF";
	ext = [".dbf",".frx"];
	forbidExtMatch = true;
	magic = [{},"dBASE Database",{},"Table MS Visual FoxPro","FoxPro with memo DBF"];
	converters = [{"program":"soffice","flags":{"sofficeType":"csv"}},"strings"]
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "dBase/FoxBase/XBase Database File",
	website        : "http://fileformats.archiveteam.org/wiki/DBF",
	ext            : [".dbf", ".frx"],
	forbidExtMatch : true,
	magic          : [/^(?:FoxBase\+?\/?)?dBase .*DBF/, "dBASE Database", /^xBase .*DBF/, "Table MS Visual FoxPro", "FoxPro with memo DBF"],
};

exports.converterPriority = [{program : "soffice", flags : {sofficeType : "csv"}}, "strings"];

*/
