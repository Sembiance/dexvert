/*
import {Program} from "../../Program.js";

export class PageStream extends Program
{
	website = "https://pagestream.org/";
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website : "https://pagestream.org/"
};

exports.qemu = () => "c:\\PageStream\\PageStream5.exe";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.qemuData = (state, p, r) => ({
	inFilePaths : [r.args[0]],
	script : `
		WinWaitActive("Select Module...", "", 10)
		ControlClick("Select Module...", "", "[CLASS:Button; TEXT:OK]")

		WinWaitActive("Font Substitution", "", 10)
		ControlClick("Font Substitution", "", "[CLASS:Button; TEXT:OK]")

		Sleep(500)
		Send("!f")
		Sleep(100)
		Send("D")
		Sleep(100)

		WinWaitActive("Save As PDF", "", 10)
		ControlClick("Save As PDF", "", "[CLASS:Button; TEXT:Save]")

		Send("c:\\out\\out.pdf{ENTER}")

		WinWaitClose("Save As PDF", "", 10)

		Sleep(200)
		
		Send("^q")`
});

exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "out.pdf"), path.join(state.output.absolute, `${state.input.name}.pdf`))(state, p, cb);
*/
