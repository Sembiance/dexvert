/*
import {Format} from "../../Format.js";

export class dng extends Format
{
	name = "Digital Negative";
	website = "http://fileformats.archiveteam.org/wiki/DNG";
	ext = [".dng"];
	mimeType = "image/x-adobe-dng";
	magic = ["TIFF image data"];
	weakMagic = true;
	converters = ["darktable-cli","convert","abydosconvert","nconvert"]

inputMeta = undefined;
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "Digital Negative",
	website   : "http://fileformats.archiveteam.org/wiki/DNG",
	ext       : [".dng"],
	mimeType  : "image/x-adobe-dng",
	magic     : ["TIFF image data"],
	weakMagic : true
};

exports.converterPriority = ["darktable-cli", "convert", "abydosconvert", "nconvert"];

exports.inputMeta = (state, p, cb) => p.family.darkTableInputMeta(state, p, cb);

*/