/*
import {Format} from "../../Format.js";

export class wav extends Format
{
	name = "Waveform Audio File Format";
	website = "http://fileformats.archiveteam.org/wiki/WAV";
	ext = [".wav"];
	mimeType = "audio/x-wav";
	magic = ["RIFF/WAVe standard Audio",{},"Waveform Audio (PCMWAVEFORMAT)"];
	converters = ["ffmpeg"]

inputMeta = undefined;
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Waveform Audio File Format",
	website  : "http://fileformats.archiveteam.org/wiki/WAV",
	ext      : [".wav"],
	mimeType : "audio/x-wav",
	magic    : ["RIFF/WAVe standard Audio", /^RIFF.* WAVE audio/, "Waveform Audio (PCMWAVEFORMAT)"]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["ffmpeg"];

*/
