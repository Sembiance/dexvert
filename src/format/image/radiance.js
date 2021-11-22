/*
import {Format} from "../../Format.js";

export class radiance extends Format
{
	name = "Radiance HDR";
	website = "http://fileformats.archiveteam.org/wiki/Radiance_HDR";
	ext = [".hdr",".rgbe",".xyze",".pic",".rad"];
	mimeType = "image/vnd.radiance";
	magic = ["Radiance RGBE Image Format","Radiance HDR image data","Radiance High Dynamic Range bitmap"];
	slow = true;
	converters = ["pfsconvert","convert","nconvert","abydosconvert"]

inputMeta = undefined;
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name          : "Radiance HDR",
	website       : "http://fileformats.archiveteam.org/wiki/Radiance_HDR",
	ext           : [".hdr", ".rgbe", ".xyze", ".pic", ".rad"],
	mimeType      : "image/vnd.radiance",
	magic         : ["Radiance RGBE Image Format", "Radiance HDR image data", "Radiance High Dynamic Range bitmap"],
	slow          : true,
};

exports.converterPriority = ["pfsconvert", "convert", "nconvert", "abydosconvert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

*/
