"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website : "https://www.buraks.com/swifty/xena.html"
};

exports.qemu = () => "dirOpener300-850-1-PC.exe";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=state.output.absolute) => { r.inPath = inPath; r.outPath = outPath; return []; };
exports.qemuData = (state, p, r) => ({
	osid         : "winxp",
	inFilePaths  : [r.inPath],
	outDirPath   : r.outPath,
	dontMaximize : true,
	script       : `
		WinWaitActive("dirOpener300-850-1-PC", "", 10)
		Sleep(1000)
		MouseClick("left", 255, 440)

		WinWaitActive("[TITLE:Select file(s) to open]", "", 10)

		Sleep(200)
		Send("c:\\in\\${path.basename(r.inPath)}{ENTER}")
		Sleep(200)

		Local $errorVisible = WinWaitActive("[TITLE:Director Player Error]", "", 5)
		If $errorVisible Not = 0 Then
			ControlClick("[TITLE:Director Player Error]", "", "[CLASS:Button; TEXT:OK]")
		EndIf

		WaitForPID(ProcessExists("dirOpener300-850-1-PC.exe"), ${XU.MINUTE*2})`
});

exports.post = (state, p, r, cb) => p.util.file.move(path.join(r.outPath, "dirOpened output of in.cst"), path.join(r.outPath, `${state.input.name}.cst`))(state, p, cb);
