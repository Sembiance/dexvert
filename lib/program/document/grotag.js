"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	fileUtil = require("@sembiance/xutil").file;

exports.meta =
{
	website       : "http://grotag.sourceforge.net/",
	gentooPackage : "app-text/grotag",
	gentooOverlay : "dexvert"
};

exports.bin = () => "grotag";

// Grotag requires absolute paths. Might be due to the way I call the jar file, not sure.
exports.args = (state, p, r, inPath=state.input.absolute, outPath=state.output.absolute) => (["-w", inPath, outPath]);

// The CSS produced by grotag includes this ugly big great outline on all links. Let's get rid of it
exports.post = (state, p, r, cb) => fileUtil.searchReplace(path.join(state.output.absolute, "amigaguide.css"), "outline: solid gray", "", cb);
