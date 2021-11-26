/*
import {Format} from "../../Format.js";

export class raf extends Format
{
	name = "Fujifilm RAW";
	website = "http://fileformats.archiveteam.org/wiki/RAF";
	ext = [".raf"];
	magic = ["Fujifilm Raw image"];
	mimeType = "image/x-fuji-raf";
	converters = ["darktable_cli","convert",`abydosconvert[format:${this.mimeType}]`,"nconvert"]

	metaProviders = [""];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Fujifilm RAW",
	website  : "http://fileformats.archiveteam.org/wiki/RAF",
	ext      : [".raf"],
	magic    : ["Fujifilm Raw image"],
	mimeType : "image/x-fuji-raf"
};

exports.converterPriority = ["darktable_cli", "convert", `abydosconvert[format:${this.mimeType}]`, "nconvert"];

exports.inputMeta = (state, p, cb) => p.family.darkTableInputMeta(state, p, cb);

*/
