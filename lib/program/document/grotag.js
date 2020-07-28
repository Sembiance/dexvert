"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "http://grotag.sourceforge.net/",
	gentooPackage : "app-text/grotag",
	gentooOverlay : "dexvert"
};

exports.bin = () => "grotag";

// Grotag requires absolute paths. Might be due to the way I call the jar file, not sure.
exports.args = state => (["-w", state.input.absolute, path.join(state.output.absolute)]);
