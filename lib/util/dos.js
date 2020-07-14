"use strict";
const XU = require("@sembiance/xu"),
	{DOS} = require("@sembiance/xutil").dos;

// Returns a function that when called will run DOSBox with the given autoExec
exports.run = function run({autoExec, timeout=XU.MINUTE*3})
{
	return (state, p, cb) => DOS.quickOp({dosCWD : state.cwd, autoExec, timeout, verbose : state.verbose, tmpDirPath : state.tmpDirPath}, cb);
};
