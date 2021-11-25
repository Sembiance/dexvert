/*
import {Format} from "../../Format.js";

export class kodakKDC extends Format
{
	name = "Kodak RAW KDC";
	website = "http://fileformats.archiveteam.org/wiki/Kodak";
	ext = [".kdc"];
	magic = ["Kodak Digital Camera RAW image (DC serie)","Kodak Digital Camera RAW image (EasyShare serie)"];
	mimeType = "image/x-kodak-kdc";
	converters = ["darktable_cli",`abydosconvert[format:${this.mimeType}]`]

metaProviders = [""];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Kodak RAW KDC",
	website  : "http://fileformats.archiveteam.org/wiki/Kodak",
	ext      : [".kdc"],
	magic    : ["Kodak Digital Camera RAW image (DC serie)", "Kodak Digital Camera RAW image (EasyShare serie)"],
	mimeType : "image/x-kodak-kdc"
};

exports.converterPriority = ["darktable_cli", `abydosconvert[format:${this.mimeType}]`];

exports.inputMeta = (state, p, cb) => p.family.darkTableInputMeta(state, p, cb);

*/
