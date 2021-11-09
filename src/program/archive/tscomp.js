/*
import {Program} from "../../Program.js";

export class tscomp extends Program
{
	website = "http://fileformats.archiveteam.org/wiki/TSComp";
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs"),
	path = require("path");

exports.meta =
{
	website : "http://fileformats.archiveteam.org/wiki/TSComp"
};

exports.dos = () => "TSCOMP.EXE";
exports.args = (state, p, r, inPath=state.input.filePath) => (["-l", inPath, ">", "TSFILES.TXT"]);
exports.post = (state, p, r, cb) =>
{
	const tscompFilenames = fs.readFileSync(path.join(state.cwd, "TSFILES.TXT"), XU.UTF8).toString("utf8").split("\n").filter(line => line.trim().startsWith("=>")).map(line => line.trim().substring(2));
	p.util.dos.run({cmd : "TSCOMP.EXE", autoExec : tscompFilenames.map(fn => `TSCOMP.EXE -d ${state.input.filePath} ${state.output.dirPath}\\${fn}`)})(state, p, cb);
};
*/
