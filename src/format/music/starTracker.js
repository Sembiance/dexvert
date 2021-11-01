/*
import {Format} from "../../Format.js";

export class starTracker extends Format
{
	name = "Star Tracker Module";
	website = "http://fileformats.archiveteam.org/wiki/StarTrekker_/_Star_Tracker_module";
	ext = [".mod"];
	magic = [{},{}];
	forbiddenMagic = ["ASCII text","ISO-8859 text","UTF-8 Unicode text","Non-ISO extended-ASCII text","ReStructuredText file","International EBCDIC text","UTF-8 Unicode text","Printable ASCII","Unicode text, UTF-8 text","Algol 68 source, ISO-8859 text"];
	converters = ["xmp","zxtune123"]

inputMeta = undefined;
}
*/
/*
"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name           : "Star Tracker Module",
	website        : "http://fileformats.archiveteam.org/wiki/StarTrekker_/_Star_Tracker_module",
	ext            : [".mod"],
	magic          : [/^StarTrekker.* module$/, /Startracker module sound data/],
	forbiddenMagic : C.TEXT_MAGIC
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["xmp", "zxtune123"];

*/
