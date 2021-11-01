/*
import {Format} from "../../Format.js";

export class tga extends Format
{
	name = "Truevision Targa Graphic";
	website = "http://fileformats.archiveteam.org/wiki/TGA";
	ext = [".tga",".targa",".tpic",".icb",".vda",".vst"];
	mimeType = "image/x-tga";
	magic = ["Truevision TGA","Targa image data"];
	converters = ["deark","nconvert","recoil2png","abydosconvert"]

outputValidator = undefined;
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Truevision Targa Graphic",
	website  : "http://fileformats.archiveteam.org/wiki/TGA",
	ext      : [".tga", ".targa", ".tpic", ".icb", ".vda", ".vst"],
	mimeType : "image/x-tga",
	magic    : ["Truevision TGA", "Targa image data"]
};

// ImageMagick sometimes doesn't detect that a TGA image has been rotated. These other converters seem to do a better job at that
// Only deark was able to correctly handle flag_b32.tga
exports.converterPriority = ["deark", "nconvert", "recoil2png", "abydosconvert"];

// Often files are confused as TGA and it results in just a single solid image. Since TGA's don't appear to have transparecy, require more than 1 color
exports.outputValidator = (state, p, subPath, imageInfo) => imageInfo.colorCount>1;

*/
