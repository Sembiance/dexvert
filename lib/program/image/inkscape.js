"use strict";
/* eslint-disable sembiance/shorter-arrow-funs */
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website        : "https://inkscape.org/",
	gentooPackage  : "media-gfx/inkscape",
	gentooUseFlags : "cdr dbus dia exif graphicsmagick jpeg openmp postscript visio wpg"
};

exports.bin = () => "inkscape";
exports.runOptions = () => ({timeout : XU.MINUTE*2, virtualX : true});

// inkscape --actions="export-area-drawing; export-filename:/tmp/export.png; export-do;" inputFile
exports.args = state => (["--export-area-drawing", "--export-plain-svg", "--export-type=svg", "-o", "outfile.svg", state.input.filePath]);

exports.post = (state, p, cb) => p.util.file.move(path.join(state.cwd, "outfile.svg"), path.join(state.output.absolute, `${state.input.name}.svg`))(state, p, cb);

/*exports.post = (state, p, cb) =>
{
	p.util.flow.serial([
		() => ({program : "svgo", args : ["--enable=sortAttrs", "outfile.svg"]}),
		() => p.util.file.move(path.join(state.cwd, "outfile.svg"), path.join(state.output.absolute, `${state.input.name}.svg`))(state, p, cb)
	])(state, p, cb);
};*/
