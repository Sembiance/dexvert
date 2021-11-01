/*
import {Format} from "../../Format.js";

export class mid extends Format
{
	name = "MIDI Music File";
	website = "http://fileformats.archiveteam.org/wiki/MIDI";
	ext = [".mid"];
	magic = ["MIDI Music","MIDI Audio","Standard MIDI data"];
	notes = "Default instrument library used is 'eaw'. Others available: fluid, roland, creative, freepats, windows";

inputMeta = undefined;

steps = [null,null,null];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "MIDI Music File",
	website : "http://fileformats.archiveteam.org/wiki/MIDI",
	ext     : [".mid"],
	magic   : ["MIDI Music", "MIDI Audio", "Standard MIDI data"],
	notes   : "Default instrument library used is 'eaw'. Others available: fluid, roland, creative, freepats, windows"
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.steps =
[
	() => ({program : "timidity"}),
	(state, p) => p.util.file.findValidOutputFiles(true),
	(state, p) => p.family.validateOutputFiles
];

*/
