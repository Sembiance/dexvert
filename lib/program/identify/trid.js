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
exports.pre = (state, p, cb) =>
{
	state.tridTmpCWD = 	fileUtil.generateTempFilePath(state.tmpDirPath, "");
	state.tridTmpFilePath = path.join(state.tridTmpCWD, `trid${state.input.ext.toLowerCase()}`);
	fs.mkdirSync(state.tridTmpCWD, {recursive : true});
	fs.symlink(state.input.absolute, state.tridTmpFilePath, cb);
};
exports.args = state => ([state.tridTmpFilePath, "-n:5"]);
exports.post = (state, p, cb) => fileUtil.unlink(state.tridTmpCWD, cb);
