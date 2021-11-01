/*
import {Format} from "../../Format.js";

export class pbm extends Format
{
	name = "Portable Bitmap";
	website = "http://fileformats.archiveteam.org/wiki/PBM";
	ext = [".pbm"];
	mimeType = "image/x-portable-bitmap";
	magic = ["Portable BitMap","Portable Bitmap Image",{}];
	converters = ["convert"]

inputMeta = undefined;
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Portable Bitmap",
	website  : "http://fileformats.archiveteam.org/wiki/PBM",
	ext      : [".pbm"],
	mimeType : "image/x-portable-bitmap",
	magic    : ["Portable BitMap", "Portable Bitmap Image", /^Netpbm image data .*bitmap$/]
};

exports.converterPriority = ["convert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

*/
