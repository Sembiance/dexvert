/*
import {Format} from "../../Format.js";

export class fileList extends Format
{
	name = "File List";
	magic = ["ASCII text","ISO-8859 text","UTF-8 Unicode text","Non-ISO extended-ASCII text","ReStructuredText file","International EBCDIC text","UTF-8 Unicode text","Printable ASCII","Unicode text, UTF-8 text","Algol 68 source, ISO-8859 text"];
	weakMagic = true;
	priority = 3;
	ext = [".bbs",".lst",".lis",".dir",".ind"];
	filename = [{},{},{},{},{}];
	untouched = true;

idCheck = undefined;

	metaProviders = [""];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs"),
	C = require("../../C.js");

exports.meta =
{
	name      : "File List",
	magic     : C.TEXT_MAGIC,
	weakMagic : true,
	priority  : C.PRIORITY.LOW,
	ext       : [".bbs", ".lst", ".lis", ".dir", ".ind"],
	filename  : [/^dir\.?\d+$/i, /files.\d+$/i, /^files\.txt$/i, /^\d+_index.txt$/, /^[a-zA-Z]_index.txt$/],
	untouched : true
};

exports.idCheck = state => fs.statSync(state.input.absolute).size<XU.MB*25;	// Unlikely to ever encountere a file list this big

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

*/
