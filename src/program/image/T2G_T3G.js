"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website : "http://www.mindworkshop.com/gwspro.html",
	unsafe  : true
};

exports.qemu = () => "c:\\tscad4\\T2G_T3G.EXE";
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
				MouseClick("left", 462, 379, 2, 0)
				Sleep(500)
				MouseClick("left", 298, 331, 2, 0)
				WinWaitClose("[TITLE:Select source file]", "", 10)
			EndIf

			$exportVisible = WinWaitActive("[TITLE:Select target file]", "", 10)
			If $exportVisible Not = 0 Then
				Sleep(500)
				MouseClick("left", 467, 396, 2, 0)
				Sleep(500)
				Send("out.t3g{ENTER}")
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

exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "out.T3G"), path.join(state.output.absolute, `${state.input.name}.t3g`))(state, p, cb);
