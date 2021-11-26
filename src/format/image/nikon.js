/*
import {Format} from "../../Format.js";

export class nikon extends Format
{
	name = "Nikon Electronic Format";
	website = "http://fileformats.archiveteam.org/wiki/Nikon";
	ext = [".nef",".nrw"];
	magic = ["Nikon raw image",{}];
	mimeType = "image/x-nikon-nef";
	converters = ["darktable_cli","convert",`abydosconvert[format:${this.mimeType}]`,"nconvert"]

	metaProviders = [""];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Nikon Electronic Format",
	website  : "http://fileformats.archiveteam.org/wiki/Nikon",
	ext      : [".nef", ".nrw"],
	magic    : ["Nikon raw image", /^TIFF image data.*manufacturer=NIKON/],
	mimeType : "image/x-nikon-nef"
};

exports.converterPriority = ["darktable_cli", "convert", `abydosconvert[format:${this.mimeType}]`, "nconvert"];

exports.inputMeta = (state, p, cb) => p.family.darkTableInputMeta(state, p, cb);

*/
