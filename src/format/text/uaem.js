/*
import {Format} from "../../Format.js";

export class uaem extends Format
{
	name = "FS-UAE Meta File";
	website = "https://fs-uae.net/docs/options/uaem-write-flags";
	ext = [".uaem"];
	magic = ["ASCII text","ISO-8859 text","UTF-8 Unicode text","Non-ISO extended-ASCII text","ReStructuredText file","International EBCDIC text","UTF-8 Unicode text","Printable ASCII","Unicode text, UTF-8 text","Algol 68 source, ISO-8859 text","FS-UAE file metadata"];
	weakMagic = true;
	filesRequired = undefined;
	untouched = true;

	metaProvider = [""];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name          : "FS-UAE Meta File",
	website       : "https://fs-uae.net/docs/options/uaem-write-flags",
	ext           : [".uaem"],
	magic         : [...C.TEXT_MAGIC, "FS-UAE file metadata"],
	weakMagic     : true,
	filesRequired : (state, otherFiles) => otherFiles.filter(otherFile => otherFile.toLowerCase()===`${state.input.name.toLowerCase()}`),
	untouched     : true
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

*/
