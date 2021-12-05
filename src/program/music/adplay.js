/*
import {Program} from "../../Program.js";

export class adplay extends Program
{
	website = "https://github.com/adplug/adplay-unix";
	package = "media-sound/adplay";
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs"),
	fileUtil = require("@sembiance/xutil").file,
	path = require("path");

exports.meta =
{
	website       : "https://github.com/adplug/adplay-unix",
	package : "media-sound/adplay"
};

exports.bin = () => "adplay";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "outfile.wav")) => (["-O", "disk", "-d", outPath, inPath]);
exports.runOptions = () => ({timeout : XU.MINUTE*2});
exports.post = (state, p, r, cb) =>
{
	const outFilePath = path.join(state.output.absolute, "outfile.wav");
	if(!fileUtil.existsSync(outFilePath))
		return setImmediate(cb);
	
	// adplay often fails to produce a valid wav but does produce a 44 byte wav file of nothing. Let's just delete it
	if(fs.statSync(outFilePath).size===44)
		return fileUtil.unlink(outFilePath, cb);
	
	p.util.file.move(outFilePath, path.join(state.output.absolute, `${state.input.name}.wav`))(state, p, cb);
};
*/
