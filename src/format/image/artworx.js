/*
import {Format} from "../../Format.js";

export class artworx extends Format
{
	name = "ArtWorx Data Format";
	website = "http://fileformats.archiveteam.org/wiki/ArtWorx_Data_Format";
	ext = [".adf"];
	mimeType = "image/x-artworx";
	magic = [{}];
	forbiddenMagic = ["Amiga Disk image File","ASCII text","ISO-8859 text","UTF-8 Unicode text","Non-ISO extended-ASCII text","ReStructuredText file","International EBCDIC text","UTF-8 Unicode text","Printable ASCII","Unicode text, UTF-8 text","Algol 68 source, ISO-8859 text"];
	weakMagic = true;
	unsafe = true;
	converters = [{"program":"ansilove","flags":{"ansiloveType":"adf"}},"deark","abydosconvert"]

inputMeta = undefined;
}
*/
/*
"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name           : "ArtWorx Data Format",
	website        : "http://fileformats.archiveteam.org/wiki/ArtWorx_Data_Format",
	ext            : [".adf"],
	mimeType       : "image/x-artworx",
	magic          : [/^data$/],
	forbiddenMagic : ["Amiga Disk image File", ...C.TEXT_MAGIC],
	weakMagic      : true,
	unsafe         : true
};

// deark messes up several images, but ansilove seems to handle them all
exports.converterPriority = [{program : "ansilove", flags : {ansiloveType : "adf"}}, "deark", "abydosconvert"];

exports.inputMeta = (state, p, cb) => p.family.ansiArtInputMeta(state, p, cb);

*/
