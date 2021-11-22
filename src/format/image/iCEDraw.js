/*
import {Format} from "../../Format.js";

export class iCEDraw extends Format
{
	name = "iCEDraw Format";
	website = "http://fileformats.archiveteam.org/wiki/ICEDraw";
	ext = [".idf"];
	mimeType = "image/x-icedraw";
	magic = ["iCEDraw graphic"];
	forbiddenMagic = ["ASCII text","ISO-8859 text","UTF-8 Unicode text","Non-ISO extended-ASCII text","ReStructuredText file","International EBCDIC text","UTF-8 Unicode text","Printable ASCII","Unicode text, UTF-8 text","Algol 68 source, ISO-8859 text"];
	converters = [{"program":"ansilove","flags":{"ansiloveType":"idf"}},"abydosconvert"]
}
*/
/*
"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name           : "iCEDraw Format",
	website        : "http://fileformats.archiveteam.org/wiki/ICEDraw",
	ext            : [".idf"],
	mimeType       : "image/x-icedraw",
	magic          : ["iCEDraw graphic"],
	forbiddenMagic : C.TEXT_MAGIC,
};

exports.converterPriority = [{program : "ansilove", flags : {ansiloveType : "idf"}}, "abydosconvert"];

*/
