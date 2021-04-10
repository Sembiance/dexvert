"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name           : "Teletext",
	website        : "http://snisurset.net/code/abydos/teletext.html",
	ext            : [".bin"],
	forbidExtMatch : true,
	forbiddenMagic : C.TEXT_MAGIC,
	unsafe    : true,
	mimeType       : "text/x-raw-teletext",
	unsupported    : true,
	notes          : "Can't determine any reliable way to determine if a file is RAW teletext. Abydos will convert any garbage and .bin is far too generic an extension to match on."
};
