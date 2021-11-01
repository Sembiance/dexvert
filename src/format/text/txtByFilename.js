/*
import {Format} from "../../Format.js";

export class txtByFilename extends Format
{
	name = "Text File";
	website = "http://fileformats.archiveteam.org/wiki/Text";
	magic = ["ASCII text","ISO-8859 text","UTF-8 Unicode text","Non-ISO extended-ASCII text","ReStructuredText file","International EBCDIC text","UTF-8 Unicode text","Printable ASCII","Unicode text, UTF-8 text","Algol 68 source, ISO-8859 text",{}];
	weakMagic = true;
	forbidMagicMatch = true;
	priority = 4;
	filename = [{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}];
	untouched = true;
	fallback = true;

inputMeta = undefined;
}
*/
/*
"use strict";
/* eslint-disable prefer-named-capture-group */
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

// txtByFilename handles files with specific filenames that are likely text but have non-ascii characters which requires loosened magic match of /^data$/
exports.meta =
{
	name             : "Text File",
	website          : "http://fileformats.archiveteam.org/wiki/Text",
	magic            : [...C.TEXT_MAGIC, /^data$/],
	weakMagic        : true,
	forbidMagicMatch : true,	// We only ever want to match on filename
	priority         : C.PRIORITY.VERYLOW,
	filename         :
	[
		/registra.tio/i, /register.*/i,
		/descript.ion/i,
		/file_id.*\.diz/i,
		/^disk_ord.er.?$/i, /ordrform/i,
		/^(about|change|copying|description|manifest|manual|order|problems|readme|readnow|readthis|release|todo|whatsnew)[._-]*($|\..+$)/i,
		/^.*read\..*me.*$/i, /^.*read.*me.*\./i, /^.*read.?me.?$/i, /^read.*me.*$/i, /^.read_this/i, /^whats\.new$/i,
		/^.*manu.al$/i,
		/[_-]te?xt$/i
	],
	untouched : true,
	fallback  : true
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

*/
