"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website : "http://www.mindworkshop.com/gwspro.html",
	unsafe  : true
};

exports.qemu = () => "c:\\tscad4\\MPG_T2G.EXE";
exports.args = (state, p, r, inPath=state.input.filePath) => { r.inPath = inPath; };
exports.qemuData = (state, p, r) => ({
	inFilePaths : [r.inPath],
	script : `
		$mainWindowVisible = WinWaitActive("[CLASS:ConvertWClass]", "", 5)
		If $mainWindowVisible Not = 0 Then
			Send("{F2}")

			$exportVisible = WinWaitActive("[TITLE:Select source file]", "", 10)
			If $exportVisible Not = 0 Then
				Sleep(500)
				MouseClick("left", 462, 379, 1, 0)
				Sleep(500)
				Send("in.mpg{ENTER}")
				WinWaitClose("[TITLE:Select source file]", "", 10)
			EndIf

			$exportVisible = WinWaitActive("[TITLE:Select target file]", "", 10)
			If $exportVisible Not = 0 Then
				Sleep(500)
				MouseClick("left", 467, 396, 1, 0)
				Sleep(500)
				Send("out.t2g{ENTER}")
				WinWaitClose("[TITLE:Select target file]", "", 10)
			EndIf

			Sleep(500)
			Send("!f")
			Sleep(100)
			Send("x")
			Sleep(100)
;
			WinWaitClose("[CLASS:ConvertWClass]", "", 10)
		EndIf`
});

exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "OUT.T2G"), path.join(state.output.absolute, `${state.input.name}.t2g`))(state, p, cb);
