"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs"),
	fileUtil = require("@sembiance/xutil").file,
	path = require("path");

exports.meta =
{
	website : "http://aminet.net/package/util/conv/WoW"
};

exports.qemu = () => "WoW";
exports.args = (state, p, r, inPath=state.input.filePath) => (["-asc", inPath, "HD:out/outfile.txt"]);
exports.qemuData = (state, p, r) => ({osid : "amigappc", inFilePaths : [r.args[1]]});
exports.post = (state, p, r, cb) =>
{
	const outputFilePath = path.join(state.output.absolute, "outfile.txt");
	if(!fileUtil.existsSync(outputFilePath))
		return setImmediate(cb);
	
	// WoW when it fails produces files with a single newline in it, so we filter those out here
	if(fs.statSync(outputFilePath).size<=1)
		return fileUtil.unlink(outputFilePath, cb);

	p.util.file.move(outputFilePath, path.join(state.output.absolute, `${state.input.name}.txt`))(state, p, cb);
};
