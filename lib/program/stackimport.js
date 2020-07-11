"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	fileUtil = require("@sembiance/xutil").file,
	tiptoe = require("tiptoe"),
	fs = require("fs");

exports.meta =
{
	website       : "https://github.com/uliwitness/stackimport/",
	gentooPackage : "dev-util/stackimport"
};

// stackimport creates an 'in.xstk' subdir with all results
exports.bin = () => "stackimport";
exports.cwd = state => state.output.absolute;
exports.args = () => (["--dumprawblocks", "in"]);
exports.pre = (state, p, cb) => fs.symlink(state.input.absolute, path.join(state.output.absolute, "in"), cb);
exports.post = (state, p, cb) =>
{
	tiptoe(
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
