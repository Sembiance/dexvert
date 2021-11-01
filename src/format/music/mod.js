"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name           : "Protracker Module",
	website        : "http://fileformats.archiveteam.org/wiki/Amiga_Module",
	ext            : [".mod", ".ptm", ".pt36"],
	magic          : [/.*Protracker module/, "Standard 4-channel Amiga module", "ProTracker IFF module"],
	forbiddenMagic : C.TEXT_MAGIC
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = state =>
{
	const converters = ["xmp", "uade123", "mikmod2wav", "zxtune123"];

	// awaveStudio isn't safe to use, so only use it if we are a magic match
	if(state.id.matchType==="magic")
		converters.push("awaveStudio");
		
	return converters;
};
