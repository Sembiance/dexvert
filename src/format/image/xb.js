/*
import {Format} from "../../Format.js";

export class xb extends Format
{
	name = "Extended Binary";
	website = "http://fileformats.archiveteam.org/wiki/XBIN";
	ext = [".xb"];
	forbidExtMatch = true;
	mimeType = "image/x-xbin";
	magic = ["XBIN image"];
	converters = [{"program":"ansilove","flags":{"ansiloveType":"xb"}},"deark",`abydosconvert[format:${this.mimeType}]`]

	metaProvider = [""];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Extended Binary",
	website        : "http://fileformats.archiveteam.org/wiki/XBIN",
	ext            : [".xb"],
	forbidExtMatch : true,
	mimeType       : "image/x-xbin",
	magic          : ["XBIN image"],
};

exports.converterPriority = [{program : "ansilove", flags : {ansiloveType : "xb"}}, "deark", `abydosconvert[format:${this.mimeType}]`];

exports.inputMeta = (state, p, cb) => p.family.ansiArtInputMeta(state, p, cb);

*/
