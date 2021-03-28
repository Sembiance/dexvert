"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website : "https://www.irfanview.com/"
};

exports.wine = () => "IrfanView/i_view32.exe";
exports.args = (state, p, r, inPath=state.input.filePath) => ([p.util.wine.winePath(inPath), "/silent", `/convert=${p.util.wine.winePath(path.join(state.cwd, "out.png"))}`]);
exports.wineOptions = () => ({timeout : XU.MINUTE*10});

exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.cwd, "out.png"), path.join(state.output.absolute, `${state.input.name}.png`))(state, p, cb);
