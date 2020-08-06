"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website       : "http://www.watto.org/game_extractor.html",
	gentooPackage : "app-arch/gameextractor",
	gentooOverlay : "dexvert"
};

exports.bin = () => "gameextractor";
exports.args = state => (["-extract", "-input", state.input.absolute, "-output", state.output.absolute]);

// gameextractor always opens an X window (thus virtualX) and on some files it just hangs forever (thus timeout)
exports.runOptions = () => ({timeout : XU.MINUTE*2, virtualX : true});
