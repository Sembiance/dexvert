"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website : "https://archive.org/details/office97standard_201912/",
	notes   : "revisableFormText converter from: http://www.gmayor.com/downloads.htm"
};

exports.qemu = () => "c:\\Program Files\\Microsoft Office\\Office\\WINWORD.EXE";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.qemuData = (state, p, r) => ({
	inFilePaths : [r.args[0]],
	script : `
		WinWaitActive("[TITLE:Microsoft Word - ]", "", 10)

		Send("!f")
		Sleep(200)
		Send("a")

		WinWaitActive("[TITLE:Save As]", "", 10)

		Sleep(200)
		Send("c:\\out\\outfile.doc{ENTER}")
		
		WinWaitClose("[TITLE:Save As]", "", 10)
		Sleep(200)

		Send("!f")
		Sleep(200)
		Send("x")
		
		WinWaitClose("[TITLE:Microsoft Word - ]", "", 10)`
});

exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.doc"), path.join(state.output.absolute, `${state.input.name}.doc`))(state, p, cb);
