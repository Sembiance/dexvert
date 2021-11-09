/*
import {Program} from "../../Program.js";

export class cazip extends Program
{
	website = "https://support.broadcom.com/external/content/release-announcements/CAZIP.exe-CAZIPXP.exe-and-Applyptf/7844";
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website : "https://support.broadcom.com/external/content/release-announcements/CAZIP.exe-CAZIPXP.exe-and-Applyptf/7844"
};

exports.qemu = () => "cazip.exe";
exports.args = (state, p, r, inPath=state.input.filePath) => (["-u", inPath, "c:\\out\\outfile"]);
exports.qemuData = (state, p, r) => ({inFilePaths : [r.args[1]]});
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "outfile"), path.join(state.output.absolute, `${state.input.name}${state.input.ext.trimChars("_")}`))(state, p, cb);
*/
