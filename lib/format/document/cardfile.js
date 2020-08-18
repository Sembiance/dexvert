"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	name    : "MaciCardfile Document",
	website : "http://fileformats.archiveteam.org/wiki/Cardfile",
	ext     : [".crd"],
	magic   : ["Windows Cardfile database", "Cardfile"]
};

exports.steps =
[
	() => ({program : "deark"}),
	(state, p) => p.util.wine.run({cmd : "cardfile.exe", args : state.input.filePath, cwd : state.cwd, autoItScript : `
		WinActivate("[CLASS:TMain_Form]", "")
		Sleep(500)
		Send("!f")
		Sleep(250)
		Send("c")
		Sleep(250)
		Send("{ENTER}")
		Sleep(250)
		Send("!f")
		Sleep(250)
		Send("x")
		FileWrite("${path.join(state.cwd, "out.txt")}", ClipGet())`}),
	(state, p) => p.util.file.move(path.join(state.cwd, "out.txt"), path.join(state.output.absolute, `${state.input.name}.txt`))
];
