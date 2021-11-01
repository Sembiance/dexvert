"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs"),
	fileUtil = require("@sembiance/xutil").file,
	path = require("path");

exports.meta =
{
	website       : "http://zakalwe.fi/uade",
	gentooPackage : "app-emulation/uade",
	flags         :
	{
		uadeType : "Which 'player' file to use for conversion. Find a list in `ls /usr/share/uade/players/` Default: Let uade123 decide"
	}
};

exports.bin = () => "uade123";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "outfile.wav")) =>
{
	const uadeArgs = ["-e", "wav", "-f", outPath, inPath];
	if(r.flags.uadeType)
		uadeArgs.unshift("-P", `/usr/share/uade/players/${r.flags.uadeType}`);
	
	return uadeArgs;
};

exports.post = (state, p, r, cb) =>
{
	const outFilePath = path.join(state.output.absolute, "outfile.wav");
	if(!fileUtil.existsSync(outFilePath))
		return setImmediate(cb);
	
	// uade often fails to produce a valid wav but does produce a 68 byte wav file of nothing. Let's just delete it
	if(fs.statSync(outFilePath).size===68)
		return fileUtil.unlink(outFilePath, cb);
	
	p.util.file.move(outFilePath, path.join(state.output.absolute, `${state.input.name}.wav`))(state, p, cb);
};
