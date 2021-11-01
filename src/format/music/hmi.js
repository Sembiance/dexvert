/*
import {Format} from "../../Format.js";

export class hmi extends Format
{
	name = "Human Machine Interfaces MIDI Format";
	website = "http://fileformats.archiveteam.org/wiki/HMI";
	ext = [".hmi",".hmp"];
	magic = ["Human Machine Interfaces MIDI Format"];

steps = [null,null,null,null];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	name    : "Human Machine Interfaces MIDI Format",
	website : "http://fileformats.archiveteam.org/wiki/HMI",
	ext     : [".hmi", ".hmp"],
	magic   : ["Human Machine Interfaces MIDI Format"]
};

exports.steps =
[
	() => ({program : "midistar2mid"}),
	state => ({program : "timidity", argsd : [path.join(state.output.dirPath, `${state.input.name}.mid`)]}),
	(state, p) => p.util.file.findValidOutputFiles(true),
	(state, p) => p.family.validateOutputFiles
];

*/
