"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs"),
	StreamSkip = require("stream-skip"),
	path = require("path");

exports.meta =
{
	website : "https://github.com/Sembiance/dexvert",
	unsafe  : true
};

exports.args = (state, p, r, inPath=state.input.absolute, outPath=path.join(state.output.absolute, `${state.input.name}.iso`)) => ([inPath, outPath]);
exports.steps = (s0, p0, r) => [
	() => (state, p, cb) =>
	{
		// According to nrg2iso we just skip the first 307,200 bytes: http://gregory.kokanosky.free.fr/v4/linux/nrg2iso.en.html
		const inStream = fs.createReadStream(r.args[0]);
		inStream.on("error", cb);
		inStream.on("end", cb);
		inStream.pipe(new StreamSkip({skip : 307200})).pipe(fs.createWriteStream(r.args[1]));
	}
];
