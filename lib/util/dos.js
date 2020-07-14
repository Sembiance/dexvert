"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs"),
	path = require("path"),
	{DOS} = require("@sembiance/xutil").dos;

// Returns a function that when called will run DOSBox with the given autoExec
exports.run = function run({p, autoExec, bin, timeout=XU.MINUTE*3, screenshot, keys, keyOpts})
{
	return p.util.flow.serial([
		() => (subState, subP, cb) => (bin ? fs.symlink(path.join(__dirname, "..", "..", "dos", bin), path.join(subState.cwd, bin), cb) : setImmediate(cb)),
		() => (subState, subP, cb) => DOS.quickOp({dosCWD : subState.cwd, autoExec, timeout, verbose : subState.verbose, tmpDirPath : subState.tmpDirPath, screenshot, keys, keyOpts}, cb)
	]);
};
