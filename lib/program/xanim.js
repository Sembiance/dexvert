"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "http://xanim.polter.net/",
	gentooPackage : "media-video/xanim",
	gentooOverlay : "dexvert",
	bruteUnsafe   : true
};

exports.bin = () => "xanim";
exports.args = state => (["+Ze", "+l0", "-Zr", state.input.filePath]);
exports.runOptions = state => ({virtualX : true, recordVideoFilePath : path.join(state.output.absolute, "outfile.mp4"), timeout : XU.MINUTE*2});

exports.post = (state, p, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.mp4"), path.join(state.output.absolute, `${state.input.name}.mp4`))(state, p, cb);
