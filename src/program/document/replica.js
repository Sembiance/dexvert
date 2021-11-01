"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website : "https://gondwanaland.com/meta/history/",
	unsafe  : true
};

exports.qemu = () => "c:\\REPLICA\\REPLICA.EXE";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.qemuData = (state, p, r) => ({
	inFilePaths : [r.args[0]],
	script : `
		WinWaitActive("[CLASS:DPMDIFrameClass]", "", 20)
		
		Sleep(200)
		Send("!f")
		Sleep(200)
		Send("a")

		WinWaitActive("[TITLE:Save As]", "", 10)

		Sleep(200)
		Send("c:\\out\\out.txt{TAB}{TAB}{TAB}t{ENTER}")
		
		WinWaitClose("[TITLE:Save As]", "", 10)
		Sleep(200)

		Sleep(200)
		Send("!f")
		Sleep(200)
		Send("x")
		
		WinWaitClose("[CLASS:DPMDIFrameClass]", "", 10)`
});

exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "OUT.TXT"), path.join(state.output.absolute, `${state.input.name}.txt`))(state, p, cb);
