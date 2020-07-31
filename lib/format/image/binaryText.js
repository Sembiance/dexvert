"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Binary Text",
	website        : "http://fileformats.archiveteam.org/wiki/BIN_(Binary_Text)",
	ext            : [".bin"],
	forbidExtMatch : true,
	mimeType       : "image/x-binary",
	//magic          : [/^data$/],
	//forbiddenMagic : C.TEXT_MAGIC,
	//bruteUnsafe    : true,
	unsupported : true,
	notes       : XU.trim`
		There is no known 'magic signature' to match against. The extension '.bin' is way to generic to match on.
		Abydos and Ansilove both support this, but ansi love will convert any file you throw at it.
		So there is no known 'safe' way to convert Binary Text files to images unless you explcitly know it's such a file.
		In theory a 'negative' check could be made, where if the file contains any bytes that are normally forbidden by the format.
		But that might not even be sufficient. Due to this it won't be supported in dexvert.`
};

exports.converterPriorty = ["ansilove", "abydosconvert"];
