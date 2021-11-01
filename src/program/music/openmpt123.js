"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs"),
	fileUtil = require("@sembiance/xutil").file,
	path = require("path");

exports.meta =
{
	website       : "https://lib.openmpt.org/libopenmpt/",
	gentooPackage : "media-sound/openmpt123"
};

exports.bin = () => "openmpt123";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "outfile.wav")) => (["--batch", "--output", outPath, inPath]);

exports.post = (state, p, r, cb) =>
{
	const outFilePath = path.join(state.output.absolute, "outfile.wav");
	if(!fileUtil.existsSync(outFilePath))
		return setImmediate(cb);
	
	// adplay often fails to produce a valid wav but does produce a 88 byte wav file of nothing. Let's just delete it
	if(fs.statSync(outFilePath).size===88)
		return fileUtil.unlink(outFilePath, cb);
	
	p.util.file.move(outFilePath, path.join(state.output.absolute, `${state.input.name}.wav`))(state, p, cb);
};
