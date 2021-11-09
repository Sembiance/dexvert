/*
import {Program} from "../../Program.js";

export class 8SVXtoXXX extends Program
{
	website = "https://aminet.net/package/mus/misc/8SVXtoXXX";
	unsafe = true;
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website : "https://aminet.net/package/mus/misc/8SVXtoXXX",
	unsafe  : true
};

exports.qemu = () => "8SVXtoXXX";
exports.args = (state, p, r, inPath=state.input.filePath) => (["INPUT", inPath, "OUTPUT", "HD:out/outfile.wav"]);
exports.qemuData = (state, p, r) => ({osid : "amigappc", inFilePaths : [r.args[1]]});
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.wav"), path.join(state.output.absolute, `${state.input.name}.wav`))(state, p, cb);
*/
