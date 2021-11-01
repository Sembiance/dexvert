/*
import {Format} from "../../Format.js";

export class erf extends Format
{
	name = "Epson RAW File";
	website = "http://fileformats.archiveteam.org/wiki/ERF";
	ext = [".erf"];
	magic = ["Epson Raw Image Format",{}];
	mimeType = "image/x-epson-erf";
	converters = ["darktable-cli","convert","abydosconvert","nconvert"]

inputMeta = undefined;
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Epson RAW File",
	website  : "http://fileformats.archiveteam.org/wiki/ERF",
	ext      : [".erf"],
	magic    : ["Epson Raw Image Format", /^TIFF image data.*description=EPSON DSC/],
	mimeType : "image/x-epson-erf"
};

exports.converterPriority = ["darktable-cli", "convert", "abydosconvert", "nconvert"];

exports.inputMeta = (state, p, cb) => p.family.darkTableInputMeta(state, p, cb);

*/
