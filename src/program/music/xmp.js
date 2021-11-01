"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs"),
	fileUtil = require("@sembiance/xutil").file,
	path = require("path");

exports.meta =
{
	website        : "http://xmp.sourceforge.net/",
	gentooPackage  : "media-sound/xmp",
	gentooOverlay  : "dexvert",
	gentooUseFlags : "alsa"
};

exports.bin = () => "xmp";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "outfile.wav")) => (["-o", outPath, inPath]);

exports.post = (state, p, r, cb) =>
{
	const outFilePath = path.join(state.output.absolute, "outfile.wav");
	if(!fileUtil.existsSync(outFilePath))
		return setImmediate(cb);
	
	// xmp often fails to produce a valid wav but does produce a 44 byte wav file of nothing. Let's just delete it
	if(fs.statSync(outFilePath).size===44)
		return fileUtil.unlink(outFilePath, cb);
	
	p.util.file.move(outFilePath, path.join(state.output.absolute, `${state.input.name}.wav`))(state, p, cb);
};
