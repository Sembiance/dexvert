/*
import {Program} from "../../Program.js";

export class fastCAD extends Program
{
	website = "https://fastcad2.com/";
	unsafe = true;
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website : "https://fastcad2.com/",
	unsafe  : true
};

exports.qemu = () => "C:\\FCAD32D\\FCW32.EXE";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=state.output.absolute) => { r.inPath = inPath; r.outPath = outPath; return []; };
exports.qemuData = (state, p, r) => ({
	osid         : "winxp",
	inFilePaths  : [r.inPath],
	outDirPath   : r.outPath,
	script       : `
		WinWaitActive("[CLASS:FCW32]", "", 10)
		Send("^o")
		WinWaitActive("[TITLE:Load Drawing]", "", 10)
		Send("c:\\in\\${path.basename(r.inPath)}{ENTER}")
		WinWaitClose("[TITLE:Load Drawing]", "", 10)

		; Don't know of a better way to do this. The 'Unamed view' window is always there, and doesn't get renamed after it opens the file
		Sleep(3000)

		Send("^A")
		WinWaitActive("[TITLE:Rename & Save]", "", 10)

		Send("c:\\out\\out.bmp{TAB}b{ENTER}")

		WinWaitClose("[TITLE:Rename & Save]", "", 10)

		Sleep(500)

		ProcessClose("FCW32.EXE")
		WaitForPID(ProcessExists("FCW32.EXE"), ${XU.SECOND*10})`
});

exports.post = (state, p, r, cb) => p.util.file.move(path.join(r.outPath, "out.bmp"), path.join(r.outPath, `${state.input.name}.bmp`))(state, p, cb);
*/
