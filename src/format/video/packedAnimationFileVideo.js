/*
import {Format} from "../../Format.js";

export class packedAnimationFileVideo extends Format
{
	name = "Packed Animation File Video";
	ext = [".paf"];
	magic = ["Packed Animation File video"];
	notes = "Only 1 sample file has been located and ffmpeg (the only converter I could find) fails to process it. Submitted an ffmpeg bug: https://trac.ffmpeg.org/ticket/9362";
	converters = [{"program":"ffmpeg","flags":{"ffmpegFormat":"paf"}}]

	metaProviders = [""];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "Packed Animation File Video",
	ext   : [".paf"],
	magic : ["Packed Animation File video"],
	notes : "Only 1 sample file has been located and ffmpeg (the only converter I could find) fails to process it. Submitted an ffmpeg bug: https://trac.ffmpeg.org/ticket/9362"
};

exports.converterPriority = [{program : "ffmpeg", flags : {ffmpegFormat : "paf"}}];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

*/
