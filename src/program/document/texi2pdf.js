/*
import {Program} from "../../Program.js";

export class texi2pdf extends Program
{
	website = "https://www.gnu.org/software/texinfo/";
	package = "sys-apps/texinfo";
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://www.gnu.org/software/texinfo/",
	package : "sys-apps/texinfo"
};

exports.bin = () => "texi2pdf";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "outfile.pdf")) => (["--pdf", "--clean", `--output=${outPath}`, inPath]);
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.pdf"), path.join(state.output.absolute, `${state.input.name}.pdf`))(state, p, cb);
*/
