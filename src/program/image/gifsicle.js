"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website       : "https://www.lcdf.org/~eddietwo/gifsicle/",
	gentooPackage : "media-gfx/gifsicle",
	informational : true
};

exports.bin = () => "gifsicle";
exports.args = (state, p, r, inPath=state.input.filePath) => (["-I", inPath]);
exports.runOptions = () => ({"ignore-stderr" : true});
exports.post = (state, p, r, cb) =>
{
	const meta = {};

	if((r.results || "").trim().split("\n").some(line => line.trim().match(/^\* .+ \d+ images$/)))
		meta.animated = true;

	Object.assign(r.meta, meta);

	setImmediate(cb);
};
