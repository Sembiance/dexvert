/*
import {Format} from "../../Format.js";

export class xwd extends Format
{
	name = "X Window Dump";
	website = "http://fileformats.archiveteam.org/wiki/XWD";
	ext = [".xwd",".dmp"];
	safeExt = undefined;
	mimeType = "image/x-xwindowdump";
	magic = ["X-Windows Screen Dump","XWD X Windows Dump image data"];
	converters = ["nconvert","abydosconvert","convert"]

inputMeta = undefined;
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "X Window Dump",
	website  : "http://fileformats.archiveteam.org/wiki/XWD",
	ext      : [".xwd", ".dmp"],
	safeExt  : () => ".xwd",
	mimeType : "image/x-xwindowdump",
	magic    : ["X-Windows Screen Dump", "XWD X Windows Dump image data"]
};

// Neither nconvert nor convert properly handle all the files, but nconvert does a little bit better with color images
exports.converterPriority = ["nconvert", "abydosconvert", "convert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

*/
