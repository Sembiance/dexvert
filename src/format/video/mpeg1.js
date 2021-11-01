/*
import {Format} from "../../Format.js";

export class mpeg1 extends Format
{
	name = "MPEG-1";
	website = "http://fileformats.archiveteam.org/wiki/MPEG-1";
	ext = [".mpg",".mp1",".mpeg",".m1v"];
	filename = [{}];
	mimeType = "video/mpeg";
	magic = ["MPEG-1 Elementary Stream","MPEG-1 Program Stream","MPEG sequence, v1"];
	converters = ["ffmpeg"]

inputMeta = undefined;
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "MPEG-1",
	website  : "http://fileformats.archiveteam.org/wiki/MPEG-1",
	ext      : [".mpg", ".mp1", ".mpeg", ".m1v"],
	filename : [/^avseq[^.]+\.dat/i],
	mimeType : "video/mpeg",
	magic    : ["MPEG-1 Elementary Stream", "MPEG-1 Program Stream", "MPEG sequence, v1"]
};

exports.converterPriority = ["ffmpeg"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

*/
