/*
import {Program} from "../../Program.js";

export class gameextractor extends Program
{
	website = "http://www.watto.org/game_extractor.html";
	package = "games-util/gameextractor";
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	fileUtil = require("@sembiance/xutil").file;

exports.meta =
{
	website       : "http://www.watto.org/game_extractor.html",
	package : "games-util/gameextractor",
};

exports.bin = () => "gameextractor";

// gameextractor requires full absolute paths
exports.args = (state, p, r, inPath=path.join(state.cwd, state.input.filePath), outPath=path.join(state.cwd, state.output.dirPath)) => (["-extract", "-input", inPath, "-output", outPath]);

// Sometimes gameextractor creates a file with a _ge_decompressed extension in the INPUT dir. Usually when it can't be identified and has no extension
exports.post = (state, p, r, cb) => fileUtil.unlink(`${state.input.absolute}_ge_decompressed`, cb);

// gameextractor always opens an X window (thus virtualX) and on some files it just hangs forever (thus timeout)
exports.runOptions = () => ({timeout : XU.MINUTE*1, virtualX : true});
*/
