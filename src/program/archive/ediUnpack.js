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
		Sleep(100)
		MouseClick("left", 316, 125, 2, 0)
		Sleep(100)
		MouseClick("left", 25, 156, 1, 0)
		Sleep(100)
		MouseClick("left", 235, 75, 1, 0)
		Sleep(1500)
		MouseClick("left", 1013, 8, 1, 0)
		Sleep(200)`
});

