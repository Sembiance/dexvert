"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs"),
	path = require("path"),
	fileUtil = require("@sembiance/xutil").file;

exports.meta =
{
	website       : "https://mark0.net/soft-trid-e.html",
	gentooPackage : "app-arch/trid",
	gentooOverlay : "dexvert",
	informational : true
};

exports.bin = () => "trid";
exports.preArgs = (state, p, r, cb) =>
{
	state.tridTmpCWD = 	fileUtil.generateTempFilePath(state.tmpDirPath, "");
	state.tridTmpFilePath = path.join(state.tridTmpCWD, `trid${state.input.ext.toLowerCase()}`);
	fs.mkdirSync(state.tridTmpCWD, {recursive : true});
	fs.symlink(state.input.absolute, state.tridTmpFilePath, cb);
};
exports.args = (state, p, r, inPath=state.tridTmpFilePath) => ([inPath, "-n:5"]);
exports.post = (state, p, r, cb) => fileUtil.unlink(state.tridTmpCWD, cb);
