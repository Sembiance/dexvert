/*
import {Format} from "../../Format.js";

export class kodakDCR extends Format
{
	name = "Kodak Pro Digital RAW";
	website = "http://fileformats.archiveteam.org/wiki/Kodak";
	ext = [".dcr"];
	magic = [{}];
	mimeType = "image/x-kodak-dcr";
	converters = ["darktable-cli","abydosconvert"]

inputMeta = undefined;
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Kodak Pro Digital RAW",
	website  : "http://fileformats.archiveteam.org/wiki/Kodak",
	ext      : [".dcr"],
	magic    : [/^TIFF image data.*manufacturer=Kodak/],
	mimeType : "image/x-kodak-dcr"
};

exports.converterPriority = ["darktable-cli", "abydosconvert"];

exports.inputMeta = (state, p, cb) => p.family.darkTableInputMeta(state, p, cb);

*/
