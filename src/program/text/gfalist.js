"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://github.com/Sembiance/gfalist",
	gentooPackage : "dev-lang/gfalist",
	gentooOverlay : "dexvert"
};

exports.bin = () => "gfalist";
exports.args = (state, p, r, inPath=state.input.filePath) => (["-f", inPath]);
//exports.post = (state, p, r, cb) => (r.results && !r.results.includes("Command failed") ? fs.writeFile(path.join(state.output.absolute, `${state.input.name}.bas`), r.results, XU.UTF8, cb) : p.util.flow.noop(cb));
exports.runOptions = state => ({"redirect-stdout" : path.join(state.output.absolute, `${state.input.name}.bas`)});
