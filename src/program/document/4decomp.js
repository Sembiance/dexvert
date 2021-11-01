"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website : "https://dosbox-x.com/wiki/Guide%3ASetting-up-networking-in-DOSBox%E2%80%90X"
};

exports.dos = () => "4DECOMP.EXE";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath, "OUT/OUTFILE.BAT"]);
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "OUTFILE.BAT"), path.join(state.output.absolute, `${state.input.name}.bat`))(state, p, cb);
