/*
import {Format} from "../../Format.js";

export class ttf extends Format
{
	name = "TrueType Font";
	website = "http://fileformats.archiveteam.org/wiki/TTF";
	ext = [".ttf"];
	magic = ["TrueType Font","TrueType Font data"];
	untouched = true;

steps = [null];

metaProviders = [""];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "TrueType Font",
	website   : "http://fileformats.archiveteam.org/wiki/TTF",
	ext       : [".ttf"],
	magic     : ["TrueType Font", "TrueType Font data"],
	untouched : true
};

exports.steps = [(state, p) => p.util.flow.serial(p.family.previewSteps)];
exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

*/
