/*
import {Format} from "../../Format.js";

export class pentaxRaw extends Format
{
	name = "Pentax RAW";
	website = "http://fileformats.archiveteam.org/wiki/Pentax_PEF";
	ext = [".pef",".ptx"];
	magic = ["Pentax RAW image"];
	mimeType = "image/x-pentax-pef";
	converters = ["darktable_cli","convert",`abydosconvert[format:${this.mimeType}]`,"nconvert"]

	metaProviders = [""];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Pentax RAW",
	website  : "http://fileformats.archiveteam.org/wiki/Pentax_PEF",
	ext      : [".pef", ".ptx"],
	magic    : ["Pentax RAW image"],
	mimeType : "image/x-pentax-pef"
};

exports.converterPriority = ["darktable_cli", "convert", `abydosconvert[format:${this.mimeType}]`, "nconvert"];

exports.inputMeta = (state, p, cb) => p.family.darkTableInputMeta(state, p, cb);

*/
