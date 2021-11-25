/*
import {Format} from "../../Format.js";

export class cr2 extends Format
{
	name = "Canon RAW 2";
	website = "http://fileformats.archiveteam.org/wiki/Canon_RAW_2";
	ext = [".cr2"];
	magic = ["Canon RAW 2 format","Canon CR2 raw image data"];
	mimeType = "image/x-canon-cr2";
	converters = ["darktable_cli","convert",`abydosconvert[format:${this.mimeType}]`,"nconvert"]

metaProviders = [""];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Canon RAW 2",
	website  : "http://fileformats.archiveteam.org/wiki/Canon_RAW_2",
	ext      : [".cr2"],
	magic    : ["Canon RAW 2 format", "Canon CR2 raw image data"],
	mimeType : "image/x-canon-cr2"
};

exports.converterPriority = ["darktable_cli", "convert", `abydosconvert[format:${this.mimeType}]`, "nconvert"];

exports.inputMeta = (state, p, cb) => p.family.darkTableInputMeta(state, p, cb);

*/
