/*
import {Program} from "../../Program.js";

export class CADDraw extends Program
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

exports.qemu = () => "c:\\tscad4\\RELEASE4.EXE";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.qemuData = (state, p, r) => ({
	inFilePaths : [r.args[0]],
	script : `
		$mainWindowVisible = WinWaitActive("[CLASS:MainWClassToso4]", "", 5)
		If $mainWindowVisible Not = 0 Then
			Sleep(500)
			Send("!f")
			Sleep(100)
			Send("a")
			Sleep(100)

			$exportVisible = WinWaitActive("[TITLE:Save Drawing as...]", "", 10)
			If $exportVisible Not = 0 Then
				Send("c:\\out\\out.wmf{TAB}w{ENTER}")

				WinWaitClose("Save Drawing as...", "", 10)

				$messageVisible = WinWaitActive("[TITLE:Message]", "", 10)
				If $messageVisible Not = 0 Then
					ControlClick("[TITLE:Message]", "", "[CLASS:Button; TEXT:&Yes]")
					WinWaitClose("Message", "", 10)
				EndIf
			EndIf

			Sleep(500)
			Send("!f")
			Sleep(100)
			Send("x")
			Sleep(100)

			WinWaitClose("[CLASS:MainWClassToso4]", "", 10)
		EndIf`
});

exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "out.wmf"), path.join(state.output.absolute, `${state.input.name}.wmf`))(state, p, cb);
*/
