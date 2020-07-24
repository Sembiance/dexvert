"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Binary Text",
	website        : "http://fileformats.archiveteam.org/wiki/BIN_(Binary_Text)",
	//ext            : [".bin"],
	//forbidExtMatch : true,
	mimeType       : "image/x-binary",
	//magic          : [/^data$/],
	//forbiddenMagic : C.TEXT_MAGIC,
	//bruteUnsafe    : true,
	unsupported    : true,
	unsupportedNotes : XU.trim`
		There is no known 'signature' to have a magic match against. The extension is way to generic to match on. And the converter programs will convert anything you throw at it.
		So while abydos and ansilove support this, it's not safe to actually try and convert.`
};

exports.converterPriorty = ["ansilove", "abydosconvert"];
