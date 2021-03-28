"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website : "http://www.mindworkshop.com/gwspro.html"
};

exports.wine = () => "C:/Program Files (x86)/Alchemy Mindworks/Graphic Workshop Professional 11/gwspro.exe";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);

exports.wineOptions = (state, p) => ({
	isolate      : true,
	autoItScript : `
		WinActivate("[CLASS:GraphicsWorkshopStandAloneViewClass]", "")
		Sleep(500)
		Send("^s")
		Sleep(500)
		Send("${p.util.wine.winePath(path.join(state.cwd, "out.png"))}")
		Sleep(500)
		Send("{ENTER}")
		Sleep(500)
		Send("{ESCAPE}")`
});

exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.cwd, "out.png"), path.join(state.output.absolute, `${state.input.name}.png`))(state, p, cb);
