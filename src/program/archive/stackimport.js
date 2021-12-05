/*
import {Program} from "../../Program.js";

export class stackimport extends Program
{
	website = "https://github.com/uliwitness/stackimport/";
	package = "dev-util/stackimport";
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	fileUtil = require("@sembiance/xutil").file,
	tiptoe = require("tiptoe"),
	fs = require("fs");

exports.meta =
{
	website       : "https://github.com/uliwitness/stackimport/",
	package : "dev-util/stackimport"
};

exports.bin = () => "stackimport";
exports.args = (state, p, r, inPath="in") => (["--dumprawblocks", inPath]);
exports.cwd = state => state.output.absolute;
// We never want an extension when using this program
exports.pre = (state, p, r, cb) => fs.symlink(state.input.absolute, path.join(state.output.absolute, "in"), cb);
exports.post = (state, p, r, cb) =>
{
	// stackimport creates an 'in.xstk' subdir with all results
	tiptoe(
		function removeInSymlink()
		{
			fileUtil.unlink(path.join(state.output.absolute, "in"), this);
		},
		function moveOutputFiles()
		{
			p.util.file.moveAllFiles(path.join(state.output.absolute, "in.xstk"), state.output.absolute)(state, p, this);
		},
		function removeGeneratedDir()
		{
			fileUtil.unlink(path.join(state.output.absolute, "in.xstk"), this);
		},
		cb
	);
};
*/
