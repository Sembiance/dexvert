/*
import {Program} from "../../Program.js";

export class wordStar extends Program
{
	website = "https://en.wikipedia.org/wiki/WordStar";
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website : "https://en.wikipedia.org/wiki/WordStar"
};

exports.qemu = () => "c:\\WSWIN\\WSWIN.EXE";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.qemuData = (state, p, r) => ({
	inFilePaths : [r.args[0]],
	script : `
		WinWaitActive("[TITLE:WSWin 2.0]", "", 10)

		Sleep(1000)

		$warningVisible = WinWaitActive("[TITLE:Warning]", "", 5)
		If $warningVisible Not = 0 Then
			Send("{ENTER}")
		EndIf

		$noPrinterVisible = WinWaitActive("[TITLE:WSWin 2.0]", "No printer is installed", 5)
		If $noPrinterVisible Not = 0 Then
			Send("{ENTER}")
		EndIf

		Send("^+e")

		WinWaitActive("[TITLE:Export]", "", 10)

		Sleep(200)
		Send("c:\\out\\out.txt{TAB}{TAB}{TAB}{TAB}ansi{ENTER}")
		WinWaitClose("[TITLE:Export]", "", 10)

		Send("^q")

		$saveChangesVisible = WinWaitActive("[TITLE:WSWin 2.0]", "Do you want to save", 5)
		If $saveChangesVisible Not = 0 Then
			Send("n")
		EndIf
		
		WinWaitClose("[TITLE:WSWin 2.0]", "", 10)`
});

exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "OUT.TXT"), path.join(state.output.absolute, `${state.input.name}.txt`))(state, p, cb);
*/
