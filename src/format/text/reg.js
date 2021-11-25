/*
import {Format} from "../../Format.js";

export class reg extends Format
{
	name = "Windows Registry Data";
	website = "http://fileformats.archiveteam.org/wiki/Windows_Registry";
	ext = [".reg",".dat"];
	forbidExtMatch = true;
	magic = [{}];
	untouched = true;

metaProviders = [""];
}
*/
/*
"use strict";
/* eslint-disable prefer-named-capture-group */
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Windows Registry Data",
	website        : "http://fileformats.archiveteam.org/wiki/Windows_Registry",
	ext            : [".reg", ".dat"],
	forbidExtMatch : true,
	magic          : [/^Windows Registry (Data|text)/],
	untouched      : true
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

*/
