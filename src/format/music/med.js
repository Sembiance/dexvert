/*
import {Format} from "../../Format.js";

export class med extends Format
{
	name = "OctaMED Module";
	website = "http://fileformats.archiveteam.org/wiki/MED";
	ext = [".med",".mmd1",".mmd2",".mmd3",".mmd4",".mmdc"];
	magic = ["OctaMED Pro music file",{},"OctaMED Music Editor module","MED_Song","OctaMED Soundstudio music file","MED music file"];
	converters = ["xmp","openmpt123","zxtune123","uade123"]

	metaProvider = [""];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "OctaMED Module",
	website : "http://fileformats.archiveteam.org/wiki/MED",
	ext     : [".med", ".mmd1", ".mmd2", ".mmd3", ".mmd4", ".mmdc"],
	magic   : ["OctaMED Pro music file", /OctaMED MMD[0123C] module/, "OctaMED Music Editor module", "MED_Song", "OctaMED Soundstudio music file", "MED music file"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["xmp", "openmpt123", "zxtune123", "uade123"];

*/
