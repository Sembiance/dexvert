/*
import {Program} from "../../Program.js";

export class T3G_T4G extends Program
{
	website = "http://www.mindworkshop.com/gwspro.html";
	unsafe = true;
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website : "http://www.mindworkshop.com/gwspro.html",
	unsafe  : true
};

exports.qemu = () => "c:\\tscad4\\T3G_T4G.EXE";
exports.args = (state, p, r, inPath=state.input.filePath) => [inPath];
exports.qemuData = (state, p, r) => ({
	inFilePaths : [r.args[0]],
	script : `
		$mainWindowVisible = WinWaitActive("[CLASS:ConvertWClass]", "", 5)
		If $mainWindowVisible Not = 0 Then
			Send("{F2}")

			$exportVisible = WinWaitActive("[TITLE:Select source file]", "", 10)
			If $exportVisible Not = 0 Then
				Send("c:\\in{ENTER}")
				Sleep(200)
				Send("{TAB}{DOWN}{ENTER}")
				WinWaitClose("[TITLE:Select source file]", "", 10)
			EndIf

			$exportVisible = WinWaitActive("[TITLE:Select target file]", "", 10)
			If $exportVisible Not = 0 Then
				Send("c:\\out{ENTER}")
				Sleep(200)
				Send("out.t4g{ENTER}")
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

exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "out.t4g"), path.join(state.output.absolute, `${state.input.name}.t4g`))(state, p, cb);
*/
