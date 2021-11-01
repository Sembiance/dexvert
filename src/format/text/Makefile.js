/*
import {Format} from "../../Format.js";

export class Makefile extends Format
{
	name = "Makefile";
	website = "http://fileformats.archiveteam.org/wiki/Makefile";
	ext = [".mak",".mk"];
	forbidExtMatch = true;
	filename = [{},{},{}];
	magic = ["makefile script"];
	weakMagic = true;
	untouched = true;
	hljsLang = "makefile";

inputMeta = undefined;
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Makefile",
	website        : "http://fileformats.archiveteam.org/wiki/Makefile",
	ext            : [".mak", ".mk"],
	forbidExtMatch : true,
	filename       : [/^[Mm]ake[Ff]ile[._-].*/, /^[Mm]ake[Ff]ile$/, /.*[Mm]ake[Ff]ile$/],
	magic          : ["makefile script"],
	weakMagic      : true,
	untouched      : true,
	hljsLang       : "makefile"
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

*/
