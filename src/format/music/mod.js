/*
import {Format} from "../../Format.js";

export class mod extends Format
{
	name = "Protracker Module";
	website = "http://fileformats.archiveteam.org/wiki/Amiga_Module";
	ext = [".mod",".ptm",".pt36"];
	magic = [{},"Standard 4-channel Amiga module","ProTracker IFF module"];
	forbiddenMagic = ["ASCII text","ISO-8859 text","UTF-8 Unicode text","Non-ISO extended-ASCII text","ReStructuredText file","International EBCDIC text","UTF-8 Unicode text","Printable ASCII","Unicode text, UTF-8 text","Algol 68 source, ISO-8859 text"];
	converters = undefined

	metaProviders = [""];
}
*/
/*
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

*/
