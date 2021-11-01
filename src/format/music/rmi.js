/*
import {Format} from "../../Format.js";

export class rmi extends Format
{
	name = "RIFF MIDI Music";
	website = "http://fileformats.archiveteam.org/wiki/RIFF_MIDI";
	ext = [".rmi"];
	magic = ["RMI RIFF MIDI Music","RIFF-based MIDI",{}];

inputMeta = undefined;

steps = [null,null,null];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "RIFF MIDI Music",
	website : "http://fileformats.archiveteam.org/wiki/RIFF_MIDI",
	ext     : [".rmi"],
	magic   : ["RMI RIFF MIDI Music", "RIFF-based MIDI", /^RIFF.* data, MIDI$/]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.steps =
[
	() => ({program : "timidity"}),
	(state, p) => p.util.file.findValidOutputFiles(true),
	(state, p) => p.family.validateOutputFiles
];

*/
