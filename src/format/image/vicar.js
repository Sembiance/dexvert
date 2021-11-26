/*
import {Format} from "../../Format.js";

export class vicar extends Format
{
	name = "Video Image Communication and Retrieval";
	website = "http://fileformats.archiveteam.org/wiki/VICAR";
	ext = [".vicar",".vic",".img"];
	mimeType = "image/x-vicar";
	magic = ["VICAR JPL image bitmap","PDS (VICAR) image data"];
	converters = ["convert",`abydosconvert[format:${this.mimeType}]`]

	metaProviders = [""];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Video Image Communication and Retrieval",
	website  : "http://fileformats.archiveteam.org/wiki/VICAR",
	ext      : [".vicar", ".vic", ".img"],
	mimeType : "image/x-vicar",
	magic    : ["VICAR JPL image bitmap", "PDS (VICAR) image data"]
};

exports.converterPriority = ["convert", `abydosconvert[format:${this.mimeType}]`];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

*/
