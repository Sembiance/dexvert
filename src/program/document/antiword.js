"use strict";
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	fs = require("fs"),
	path = require("path");

exports.meta =
{
	website       : "http://www.winfield.demon.nl",
	gentooPackage : "app-text/antiword"
};

exports.bin = () => "antiword";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.redirectOutput = state => path.join(state.output.absolute, `${state.input.name}.txt`);
exports.post = (state, p, r, cb) =>
{
	const outFilePath = path.join(state.output.absolute, `${state.input.name}.txt`);

	if(((r || {}).results || "").toLowerCase().includes("encrypted documents are not supported"))
	{
		Object.assign(r.meta, {passwordProtected : true});
		return fileUtil.unlink(outFilePath, cb);
	}

	if(fs.statSync(outFilePath).size<=2)
		return fileUtil.unlink(outFilePath, cb);

	setImmediate(cb);
};
