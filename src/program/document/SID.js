/*
import {Program} from "../../Program.js";

export class SID extends Program
{
	website = "https://github.com/tylerapplebaum/setupinxhacking";
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website : "https://github.com/tylerapplebaum/setupinxhacking"
};

exports.qemu = () => "c:\\dexvert\\SID\\sid.exe";
exports.args = (state, p, r, inPath=state.input.filePath) => { r.inPath = inPath; };
exports.qemuData = (state, p, r) => ({
	inFilePaths : [r.inPath],
	script : `
		WinWaitActive("[sid] sexy installshield decompiler", "", 10)

		Sleep(500)
		Send("!f")
		Sleep(100)
		Send("o")
		Sleep(100)

		WinWaitActive("Choose file to decompile", "", 10)
		Sleep(200)
		Send("c:\\in\\${path.basename(r.inPath)}{ENTER}")
		WinWaitClose("Choose file to decompile", "", 10)

		Local $winHandle = WinGetHandle("[sid] sexy installshield decompiler")

		; Wait for the the progress bar to fill up
		Local $pixelColor
		Local $timer = TimerInit()
		Do
			$pixelColor = PixelGetColor(1015, 729, $winHandle)
			If Hex($pixelColor) == "00000080" Then ExitLoop
			Sleep(50)
		Until TimerDiff($timer) > ${XU.MINUTE*2}

		Sleep(${XU.SECOND*10})

		ClipPut("")
		Send("^a")
		Sleep(50)
		Send("^c")
		WaitForClipChange(${XU.SECOND})
		FileWrite("c:\\out\\out.txt", ClipGet())

		Sleep(500)
		Send("!f")
		Sleep(100)
		Send("q")
		Sleep(100)
		
		WinWaitClose("[sid] sexy installshield decompiler", "", 10)`
});

exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "out.txt"), path.join(state.output.absolute, `${state.input.name}.txt`))(state, p, cb);
*/
