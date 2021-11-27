import {Format} from "../../Format.js";

export class ige extends Format
{
	name       = "Interlace Graphics Editor";
	website    = "http://fileformats.archiveteam.org/wiki/Interlace_Graphics_Editor";
	ext        = [".ige"];
	converters = ["recoil2png"]
}

/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Interlace Graphics Editor",
	website : "http://fileformats.archiveteam.org/wiki/Interlace_Graphics_Editor",
	ext     : [".ige"]
};

exports.converterPriority = ["recoil2png"];

*/
