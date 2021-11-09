/*
import {Program} from "../../Program.js";

export class cardfile extends Program
{
	website = "http://www.geert.com/CardFile.htm";
	unsafe = true;
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website : "http://www.geert.com/CardFile.htm",
	unsafe  : true
};

exports.qemu = () => "cardfile.exe";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.qemuData = (state, p, r) => ({
	inFilePaths : [r.args[0]],
	script : `
		$mainWindowVisible = WinWaitActive("[CLASS:TMain_Form]", "", 7)
		If $mainWindowVisible = 0 Then
			$errorVisible = WinWaitActive("[TITLE:CardFile by GEERT.COM]", "", 7)
			If $errorVisible Not = 0 Then
				ControlClick("[TITLE:CardFile by GEERT.COM]", "", "[CLASS:Button; TEXT:OK]")
			EndIf

			WinWaitActive("[CLASS:TMain_Form]", "", 7)
		Else
			Send("^p")

			WinWaitActive("[CLASS:TMessageForm; TITLE:Information]", "", 30)

			ControlClick("[CLASS:TMessageForm; TITLE:Information]", "", "[CLASS:TButton; TEXT:OK]")
			FileWrite("c:\\out\\out.txt", ClipGet())
		EndIf

		Send("!f")
		Sleep(200)
		Send("x")`
});

exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "out.txt"), path.join(state.output.absolute, `${state.input.name}.txt`))(state, p, cb);
*/
