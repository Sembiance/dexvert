/*
import {Program} from "../../Program.js";

export class MDFtoISO extends Program
{
	website = "http://www.mdftoiso.com/";
	unsafe = true;
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website : "http://www.mdftoiso.com/",
	unsafe  : true
};

exports.qemu = () => "c:\\Program Files\\MDF to ISO\\mdftoiso.exe";
exports.args = (state, p, r, inPath=state.input.filePath) => { r.inPath = inPath; return []; };
exports.qemuData = (state, p, r) => ({
	osid         : "winxp",
	inFilePaths : [r.inPath],
	script : `
		WinWaitActive("MDF to ISO", "", 10)

		ControlSetText("MDF to ISO", "", "[CLASS:TEdit; INSTANCE:2]", "c:\\in\\${path.basename(r.inPath)}")
		ControlSetText("MDF to ISO", "", "[CLASS:TEdit; INSTANCE:1]", "c:\\out\\out.iso")

		Sleep(1000)

		ControlClick("MDF to ISO", "", "[CLASS:TButton; TEXT:Convert]")

		Local $isComplete = WinWaitActive("Information", "", 30)
		If $isComplete Then
			ControlClick("Information", "", "[CLASS:TButton; TEXT:OK]")
		EndIf

		WinWaitActive("MDF to ISO", "", 10)
		ControlClick("MDF to ISO", "", "[CLASS:TButton; TEXT:Close]")

		WinWaitClose("MDF to ISO", "", 10)

		ProcessWaitClose("mdftoiso.exe", 10)`
});

exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "out.iso"), path.join(state.output.absolute, `${state.input.name}.iso`))(state, p, cb);
*/
