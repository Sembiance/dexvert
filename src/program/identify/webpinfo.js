/*
import {Program} from "../../Program.js";

export class webpinfo extends Program
{
	website = "https://developers.google.com/speed/webp/download";
	gentooPackage = "media-libs/libwebp";
	gentooUseFlags = "gif jpeg opengl png tiff";
	informational = true;
}
*/

/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website        : "https://developers.google.com/speed/webp/download",
	gentooPackage  : "media-libs/libwebp",
	gentooUseFlags : "gif jpeg opengl png tiff",
	informational  : true
};

exports.bin = () => "webpinfo";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.post = (state, p, r, cb) =>
{
	const meta = {};

	if((r.results || "").trim().includes("Animation: 1"))
		meta.animated = true;

	Object.assign(r.meta, meta);

	setImmediate(cb);
};
*/
