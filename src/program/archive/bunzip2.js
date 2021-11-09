/*
import {Program} from "../../Program.js";

export class bunzip2 extends Program
{
	website = "https://gitlab.com/federicomenaquintero/bzip2";
	gentooPackage = "app-arch/bzip2";
	gentooUseFlags = "split-usr";
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website        : "https://gitlab.com/federicomenaquintero/bzip2",
	gentooPackage  : "app-arch/bzip2",
	gentooUseFlags : "split-usr"
};

exports.bin = () => "bunzip2";
exports.args = (state, p, r, inPath=state.input.filePath) => (["--force", inPath]);
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.cwd, "in"), path.join(state.output.absolute, state.input.name))(state, p, cb);
*/
