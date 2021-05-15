"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website : "http://cd.textfiles.com/carousel344/003/CONV125.ZIP",
	unsafe  : true
};

exports.dos = () => "CONV125/DGIWIND.EXE";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.post = (state, p, r, cb) => p.util.program.run("recoil2png", {argsd : ["IN.MSP"]})(state, p, cb);
