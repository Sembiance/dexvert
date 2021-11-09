/*
import {Program} from "../../Program.js";

export class trid extends Program
{
	website = "https://mark0.net/soft-trid-e.html";
	gentooPackage = "app-arch/trid";
	gentooOverlay = "dexvert";
	informational = true;
}
*/

/*
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
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath, "-n:5"]);

exports.pre = (state, p, r, cb) =>
{
	state.tridTmpCWD = 	fileUtil.generateTempFilePath(undefined, "");
	state.tridTmpFilePath = path.join(state.tridTmpCWD, `trid${state.input.ext.toLowerCase()}`);
	fs.mkdirSync(state.tridTmpCWD, {recursive : true});
	const oldInputPath = r.args.splice(0, 1, state.tridTmpFilePath)[0];
	fs.symlink(oldInputPath, state.tridTmpFilePath, cb);
};

exports.post = (state, p, r, cb) => fileUtil.unlink(state.tridTmpCWD, cb);
*/
