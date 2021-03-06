"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Hypertext Markup Language File",
	website        : "http://fileformats.archiveteam.org/wiki/HTML",
	ext            : [".html", ".htm", ".xhtml", ".xht"],
	forbidExtMatch : true,
	mimeType       : "text/html",
	magic          : [/^Hyper[Tt]ext Markup Language/, /^HTML document/],
	weakMagic      : true,
	trustMagic     : true,
	untouched      : true
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
