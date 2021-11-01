"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website : "https://archive.org/details/JPEG35_ZIP",
	unsafe  : true
};

exports.dos = () => "LEADTOOL/LEADECOM.EXE";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath, "OUT.TGA", "/TGA24"]);
exports.post = (state, p, r, cb) => p.util.program.run("convert", {argsd : ["OUT.TGA"]})(state, p, cb);
