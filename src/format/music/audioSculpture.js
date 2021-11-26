/*
import {Format} from "../../Format.js";

export class audioSculpture extends Format
{
	name = "Audio Sculpture Module";
	website = "http://fileformats.archiveteam.org/wiki/Audio_Sculpture";
	ext = [".adsc"];
	magic = ["Audio Sculpture module"];
	keepFilename = true;
	filesOptional = undefined;
	converters = [{"program":"uade123","flags":{"uadeType":"AudioSculpture"}}]

	metaProviders = [""];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name          : "Audio Sculpture Module",
	website       : "http://fileformats.archiveteam.org/wiki/Audio_Sculpture",
	ext           : [".adsc"],
	magic         : ["Audio Sculpture module"],
	keepFilename  : true,
	filesOptional : (state, otherFiles) => otherFiles.filter(otherFile => otherFile.toLowerCase()===`${state.input.base.toLowerCase()}.as`)
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = [{program : "uade123", flags : {uadeType : "AudioSculpture"}}];

*/
