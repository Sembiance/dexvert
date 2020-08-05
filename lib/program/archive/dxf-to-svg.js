"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website     : "https://www.npmjs.com/package/dxf",
	bruteUnsafe : true
};

exports.bin = () => path.join(__dirname, "..", "..", "..", "node_modules", ".bin", "dxf-to-svg");
exports.args = state => ([state.input.filePath, path.join(state.output.dirPath, "outfile.svg")]);
exports.post = (state, p, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.svg"), path.join(state.output.absolute, `${state.input.name}.svg`))(state, p, cb);
