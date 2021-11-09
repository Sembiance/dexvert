/*
import {Program} from "../../Program.js";

export class Fony extends Program
{
	website = "http://hukka.ncn.fi/?fony";
}
*/

/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website : "http://hukka.ncn.fi/?fony"
};

exports.qemu = () => "Fony.exe";
exports.args = (state, p, r, inPath=state.input.base) => ([inPath]);
exports.qemuData = (state, p, r) => ({
	inFilePaths : [r.args[0], ...(state.extraFilenames || [])],
	script : `
		$errorVisible = WinWaitActive("[TITLE:Error Loading Font]", "", 10)
		If $errorVisible Not = 0 Then
			ControlClick("[TITLE:Error Loading Font]", "", "[CLASS:TBitBtn; TEXT:OK]")
		Else
			WinWaitActive("[CLASS:TFMain]", "", 30)
			Sleep(1000)
			Send("!f")
			Sleep(100)
			Send("e")
			Sleep(100)
			Send("{DOWN}")
			Sleep(100)
			Send("{ENTER}")

			$exportVisible = WinWaitActive("[CLASS:TFBDFExport; TITLE:BDF Export]", "", 7)
			If $exportVisible Not = 0 Then
				ControlClick("[CLASS:TFBDFExport]", "", "[CLASS:TButton; TEXT:OK]")

				WinWaitActive("[TITLE:Save As]", "", 30)
				ControlClick("[TITLE:Save As]", "", "[CLASS:Edit]")

				Send("{HOME}c:\\out\\")
				ControlClick("[TITLE:Save As]", "", "[CLASS:Button; TEXT:&Save]")

				WinWaitActive("[CLASS:TFMain]", "", 30)
				Sleep(200)
			EndIf

			Send("!f")
			Sleep(100)
			Send("x")
		EndIf`
});

exports.post = (state, p, r, cb) => p.util.flow.serial([
	ss => p.util.file.glob(ss.output.absolute, "*.bdf", {nodir : true}, bdfFilePaths => { r.bdfFilePath = (bdfFilePaths || [])[0]; return true; }),
	() => (r.bdfFilePath ? p.util.program.run("bdftopcf", {argsd : [r.bdfFilePath]}) : p.util.flow.noop),
	() => (r.bdfFilePath ? p.util.file.unlink(r.bdfFilePath) : p.util.flow.noop)
])(state, p, cb);
*/
