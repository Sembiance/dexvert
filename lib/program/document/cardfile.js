"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website : "http://www.geert.com/CardFile.htm"
};

exports.qemu = () => "cardfile.exe";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.qemuData = (state, p, r) => ({
	inFilePaths : [r.args[0]],
	autoIt : `
		WinWaitActive("[CLASS:TMain_Form]")
		WinActivate("[CLASS:TMain_Form]")
		Send("^p")

		WinWaitActive("[CLASS:TMessageForm; TITLE:Information]")
		WinActivate("[CLASS:TMessageForm; TITLE:Information]")

		ControlClick("[CLASS:TMessageForm; TITLE:Information]", "", "[CLASS:TButton; TEXT:OK]")
		FileWrite("c:\\out\\out.txt", ClipGet())

		Send("!f")
		Sleep(200)
		Send("x")`
});

exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "out.txt"), path.join(state.output.absolute, `${state.input.name}.txt`))(state, p, cb);
