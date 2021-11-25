/*
import {Format} from "../../Format.js";

export class sixel extends Format
{
	name = "Sixel";
	website = "https://en.wikipedia.org/wiki/Sixel";
	ext = [".six",".sixel"];
	mimeType = "image/x-sixel";
	magic = ["ASCII text","ISO-8859 text","UTF-8 Unicode text","Non-ISO extended-ASCII text","ReStructuredText file","International EBCDIC text","UTF-8 Unicode text","Printable ASCII","Unicode text, UTF-8 text","Algol 68 source, ISO-8859 text"];
	weakMagic = true;
	converters = [`abydosconvert[format:${this.mimeType}]`]
}
*/
/*
"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name      : "Sixel",
	website   : "https://en.wikipedia.org/wiki/Sixel",
	ext       : [".six", ".sixel"],
	mimeType  : "image/x-sixel",
	magic     : C.TEXT_MAGIC,
	weakMagic : true
};

exports.converterPriority = [`abydosconvert[format:${this.mimeType}]`];

*/
