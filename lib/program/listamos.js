"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	fs = require("fs");

exports.meta =
{
	website       : "https://github.com/kyz/amostools/",
	gentooPackage : "dev-lang/amostools",
	gentooOverlay : "dexvert"
};

// stackimport creates an 'in.xstk' subdir with all results
exports.bin = () => "listamos";
exports.cwd = state => state.output.absolute;
exports.args = state => ([state.input.filePath]);
exports.post = (state, p, cb) =>
{
	const sourceCode = (state.run.listamos || [""])[0].trim();
	if(sourceCode.length===0 || sourceCode.endsWith("not an AMOS source file"))
		return setImmediate(cb);
	
	fs.writeFile(path.join(state.output.absolute, state.input.name + "_sourceCode"), sourceCode.trim(), XU.UTF8, cb);
};
