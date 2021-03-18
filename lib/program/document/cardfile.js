"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website : "http://www.geert.com/CardFile.htm"
};

exports.wine = () => "cardfile.exe";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.wineOptions = state => ({
	isolate      : true,	// Required due to only being able to use the clipboard to get the contents, which is shared by wineserver
	autoItScript : `
		WinActivate("[CLASS:TMain_Form]", "")
		Sleep(500)
		Send("!f")
		Sleep(500)
		Send("c")
		Sleep(500)
		Send("{ENTER}")
		Sleep(500)
		Send("!f")
		Sleep(500)
		Send("x")
		FileWrite("${path.join(state.cwd, "out.txt")}", ClipGet())`
});

exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.cwd, "out.txt"), path.join(state.output.absolute, `${state.input.name}.txt`))(state, p, cb);
