"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website : "https://github.com/Sembiance/dexvert/blob/master/qemu/win2k/data/app/UNPACK.EXE"
};

exports.qemu = () => "c:\\dexvert\\UNPACK.exe";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);

exports.qemuData = (state, p, r) => ({
	cwd : "c:\\in",
	inFilePaths : [r.args.last()],
	// Sadly, the program crashes instantly as soon as I try and use AutoIt window info to find buttons, so we resort to X/Y screen coordinates and cross our fingers
	script : `
		Sleep(2000)
		MouseClick("left", 316, 86, 2, 0)
		Sleep(1000)
		MouseClick("left", 316, 125, 2, 0)
		Sleep(1000)
		MouseClick("left", 25, 156, 1, 0)
		Sleep(1000)
		MouseClick("left", 235, 75, 1, 0)
		Sleep(1000)
		MouseClick("left", 1013, 8, 1, 0)
		Local $errorOKControl = WaitForControl("[TITLE:in$]", "", "[CLASS:Button; TEXT:OK]", ${XU.SECOND*3})
		If $errorOKControl Then
			ControlClick("[TITLE:in$]", "", "[CLASS:Button; TEXT:OK]")
		EndIf
		Sleep(5000)

		; Program tends to hang forever preventing any other instances from running, so we kill this process which kills the program
		ProcessClose("ntvdm.exe")`
});

