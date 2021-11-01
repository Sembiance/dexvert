/*
import {Format} from "../../Format.js";

export class pcd extends Format
{
	name = "Kodak Photo CD Picture";
	website = "http://fileformats.archiveteam.org/wiki/Photo_CD";
	ext = [".pcd"];
	mimeType = "image/x-photo-cd";
	magic = [{},"Kodak PhotoCD bitmap"];
	converters = ["pcdtojpeg","convert","abydosconvert","nconvert"]

inputMeta = undefined;

outputValidator = undefined;
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Kodak Photo CD Picture",
	website  : "http://fileformats.archiveteam.org/wiki/Photo_CD",
	ext      : [".pcd"],
	mimeType : "image/x-photo-cd",
	magic    : [/Kodak Photo CD [Ii]mage/, "Kodak PhotoCD bitmap"]
};

exports.converterPriority = ["pcdtojpeg", "convert", "abydosconvert", "nconvert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

// If it fails, it often produces a 2x2 or 1x1 image, so exclude those
exports.outputValidator = (state, p, subPath, imageInfo) => imageInfo.width>2 && imageInfo.height>2;

*/
