"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs"),
	fileUtil = require("@sembiance/xutil").file,
	path = require("path");

exports.meta =
{
	website       : "https://github.com/dschwen/amosbank",
	gentooPackage : "dev-lang/amosbank",
	gentooOverlay : "dexvert"
};

exports.bin = () => "amosbank";
exports.args = (state, p, inPath="in.abk") => ([inPath]);
exports.cwd = state => state.output.absolute;
exports.pre = (state, p, cb) => fs.symlink(state.input.absolute, path.join(state.output.absolute, "in.abk"), cb);
exports.post = (state, p, cb) => fileUtil.unlink(path.join(state.output.absolute, "in.abk"), cb);
