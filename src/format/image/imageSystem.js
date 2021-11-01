/*
import {Format} from "../../Format.js";

export class imageSystem extends Format
{
	name = "Image System";
	website = "http://fileformats.archiveteam.org/wiki/Image_System";
	ext = [".ish",".ism"];
	converters = ["nconvert","recoil2png","view64"]

outputValidator = undefined;
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Image System",
	website : "http://fileformats.archiveteam.org/wiki/Image_System",
	ext     : [".ish", ".ism"]
};

// recoil2png doesn't properly handle some files, nconvert does a better job here
exports.converterPriority = ["nconvert", "recoil2png", "view64"];

// Due to not having a good magic, we reject any created images that have less than 5 colors
exports.outputValidator = (state, p, subPath, imageInfo) => imageInfo.colorCount>5;

*/
