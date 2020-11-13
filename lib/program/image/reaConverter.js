"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website : "https://www.isobuster.com/isobuster.php"
};

exports.wine = () => "reaConverter/cons_rcp.exe";
exports.wineOptions = () => ({timeout : XU.MINUTE*2});

// reaConverter command line help: https://www.reaconverter.com/howto/category/command-line-2/
exports.args = (state, p, r, inPath=state.input.filePath) => (["-s", p.util.wine.path(inPath), "-o", p.util.wine.path(path.join(state.cwd, `out${r.flags.reaConverterExt || ".png"}`))]);

exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.cwd, `out${r.flags.reaConverterExt || ".png"}`), path.join(state.output.absolute, state.input.name + (r.flags.reaConverterExt || ".png")))(state, p, cb);
