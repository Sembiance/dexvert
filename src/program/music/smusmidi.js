/*
import {Program} from "../../Program.js";

export class smusmidi extends Program
{
	website = "https://aminet.net/package/mus/midi/SMUSMIDI.lha";
	unsafe = true;
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website : "https://aminet.net/package/mus/midi/SMUSMIDI.lha",
	unsafe  : true
};

// Alternative converter: https://github.com/AugusteBonnin/smus2midi
exports.qemu = () => "SMUSMIDI";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath, "HD:out/out"]);
exports.qemuData = (state, p, r) => ({osid : "amigappc", inFilePaths : [r.args[0]]});
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "out.MID"), path.join(state.output.absolute, `${state.input.name}.mid`))(state, p, cb);
*/
