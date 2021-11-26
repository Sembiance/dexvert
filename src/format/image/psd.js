/*
import {Format} from "../../Format.js";

export class psd extends Format
{
	name = "Adobe Photoshop";
	website = "http://fileformats.archiveteam.org/wiki/PSD";
	ext = [".psd"];
	mimeType = "image/vnd.adobe.photoshop";
	magic = [{},{}];
	converters = ["convert"]

	metaProviders = [""];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Adobe Photoshop",
	website  : "http://fileformats.archiveteam.org/wiki/PSD",
	ext      : [".psd"],
	mimeType : "image/vnd.adobe.photoshop",
	magic    : [/^Adobe Photoshop [Ii]mage/, /^Adobe Photoshop$/]
};

// I made the decision to just use regular convert, which will extract all layers from the PSD.
// I could in theory just extract the 'main' image by doing: {program : "convert", argsd : [`${state.input.filePath}[0]`]}
exports.converterPriority = ["convert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);


*/
