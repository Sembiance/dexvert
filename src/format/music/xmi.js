/*
import {Format} from "../../Format.js";

export class xmi extends Format
{
	name = "Extended MIDI";
	website = "http://fileformats.archiveteam.org/wiki/XMI_(Extended_MIDI)";
	ext = [".xmi"];
	magic = ["Extended MIDI"];

steps = [null,null,null,null];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	name    : "Extended MIDI",
	website : "http://fileformats.archiveteam.org/wiki/XMI_(Extended_MIDI)",
	ext     : [".xmi"],
	magic   : ["Extended MIDI"]
};

exports.steps =
[
	() => ({program : "midistar2mid"}),
	state => ({program : "timidity", argsd : [path.join(state.output.dirPath, `${state.input.name}.mid`)]}),
	(state, p) => p.util.file.findValidOutputFiles(true),
	(state, p) => p.family.validateOutputFiles
];

*/