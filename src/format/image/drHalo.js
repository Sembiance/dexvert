/*
import {Format} from "../../Format.js";

export class drHalo extends Format
{
	name = "Dr. Halo";
	website = "http://fileformats.archiveteam.org/wiki/Dr._Halo";
	ext = [".cut",".pal",".pic"];
	mimeType = "application/dr-halo";
	priority = 3;
	untrustworthy = true;
	converters = ["convert","recoil2png","abydosconvert"]

inputMeta = undefined;

outputValidator = undefined;	// Rename to verify(dexFile, identifications)
}
*/
/*
"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name          : "Dr. Halo",
	website       : "http://fileformats.archiveteam.org/wiki/Dr._Halo",
	ext           : [".cut", ".pal", ".pic"],
	mimeType      : "application/dr-halo",
	priority      : C.PRIORITY.LOW,
	untrustworthy : true
};

exports.converterPriority = ["convert", "recoil2png", "abydosconvert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

// Due to not having a good magic, we reject any created images that 1 or fewer colors
exports.outputValidator = (state, p, subPath, imageInfo) => imageInfo.colorCount>1;

*/
