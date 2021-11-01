/*
import {Format} from "../../Format.js";

export class pl extends Format
{
	name = "Perl Script";
	website = "http://fileformats.archiveteam.org/wiki/Perl";
	ext = [".pl"];
	forbidExtMatch = true;
	magic = ["Perl script",{}];
	weakMagic = true;
	untouched = true;
	hljsLang = "perl";

inputMeta = undefined;
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Perl Script",
	website        : "http://fileformats.archiveteam.org/wiki/Perl",
	ext            : [".pl"],
	forbidExtMatch : true,
	magic          : ["Perl script", /^Perl\d module source/],
	weakMagic      : true,
	untouched      : true,
	hljsLang       : "perl"
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

*/
