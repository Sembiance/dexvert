/*
import {Program} from "../../Program.js";

export class sox extends Program
{
	website = "http://sox.sourceforge.net";
	gentooPackage = "media-sound/sox";
	gentooUseFlags = "alsa amr encode flac id3tag mad ogg openmp png sndfile twolame wavpack";
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website        : "http://sox.sourceforge.net",
	gentooPackage  : "media-sound/sox",
	gentooUseFlags : "alsa amr encode flac id3tag mad ogg openmp png sndfile twolame wavpack"
};

exports.bin = () => "sox";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "outfile.wav")) => ([inPath, outPath]);
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.wav"), path.join(state.output.absolute, `${state.input.name}.wav`))(state, p, cb);
*/
