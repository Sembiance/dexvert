"use strict";
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	path = require("path");

exports.meta =
{
	website : "https://github.com/Sembiance/dexvert",
	flags   :
	{
		asFormat    : `Which format to convert as`,
		deleteInput : "Delete input file after finishing"
	},
	unsafe : true
};

exports.bin = () => path.join(__dirname, "..", "..", "..", "bin", "dexvert");
exports.args = (state, p, r, inPath=state.input.filePath, outPath=state.output.dirPath) =>
{
	const dexArgs = ["--useTmpOutputDir", "--verbose", state.verbose.toString()];
	if(r.flags.asFormat)
		dexArgs.push("--asFormat", r.flags.asFormat);
	
	dexArgs.push(inPath, outPath);

	return dexArgs;
};

exports.post = (state, p, r, cb) =>
{
	if(r.flags.deleteInput)
		fileUtil.unlink(r.args.at(-2), cb);
	else
		setImmediate(cb);
};
