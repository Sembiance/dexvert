"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website       : "https://www.lcdf.org/~eddietwo/gifsicle/",
	gentooPackage : "media-gfx/gifsicle",
	informational : true
};

exports.bin = () => "gifsicle";
exports.args = (state, p, inPath=state.input.filePath) => (["-I", inPath]);
exports.runOptions = () => ({"ignore-stderr" : true});
exports.post = (state, p, cb) =>
{
	const meta = {};

	if(state.run.gifsicle[0].split("\n").some(line => line.trim().match(/^\* .+ \d+ images$/)))
		meta.animated = true;

	if(Object.keys(meta).length>0)
		state.run.meta.gifsicle = meta;

	setImmediate(cb);
};
