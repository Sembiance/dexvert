"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website       : "http://grotag.sourceforge.net/",
	gentooPackage : "app-text/grotag",
	gentooOverlay : "dexvert"
};

exports.bin = () => "grotag";

// Grotag requires absolute paths. Might be due to the way I call the jar file, not sure.
exports.args = (state, p, r, inPath=state.input.absolute, outPath=state.output.absolute) => (["-w", inPath, outPath]);
