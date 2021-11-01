/*
import {Format} from "../../Format.js";

export class smacker extends Format
{
	name = "Smacker Video";
	website = "http://fileformats.archiveteam.org/wiki/Smacker";
	ext = [".smk"];
	magic = ["Smacker movie/video (original)","Smacker Video",{}];
	converters = [{"program":"ffmpeg","flags":{"ffmpegFormat":"smk"}}]

inputMeta = undefined;
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Smacker Video",
	website  : "http://fileformats.archiveteam.org/wiki/Smacker",
	ext      : [".smk"],
	magic    : ["Smacker movie/video (original)", "Smacker Video", /^RAD Game Tools Smacker Multimedia .* frames$/]
};

exports.converterPriority = [{program : "ffmpeg", flags : {ffmpegFormat : "smk"}}];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

*/
