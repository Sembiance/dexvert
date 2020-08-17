"use strict";
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file;

exports.meta =
{
	website       : "http://www.watto.org/game_extractor.html",
	gentooPackage : "app-arch/gameextractor",
	gentooOverlay : "dexvert",
	bruteUnsafe   : true
};

exports.bin = () => "gameextractor";
exports.args = state => (["-extract", "-input", state.input.absolute, "-output", state.output.absolute]);

// Sometimes gameextractor creates a file with a _ge_decompressed extension in the INPUT dir. Usually when it can't be identified and has no extension
exports.post = (state, p, cb) => fileUtil.unlink(`${state.input.absolute}_ge_decompressed`, cb);

// gameextractor always opens an X window (thus virtualX) and on some files it just hangs forever (thus timeout)
exports.runOptions = () => ({timeout : XU.MINUTE*1, virtualX : true});
