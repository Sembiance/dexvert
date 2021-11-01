"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website : "https://www.buraks.com/swifty/xena.html",
	unsafe  : true
};

exports.qemu = () => "c:\\dexvert\\xenap14\\xenap14.exe";
exports.args = (state, p, r, inPath=state.input.filePath) => { r.inPath = inPath; return []; };
exports.qemuData = (state, p, r) => ({
	inFilePaths : [r.inPath],
	script : `
		FileCopy("c:\\in\\${path.basename(r.inPath)}", "c:\\out\\${path.basename(r.inPath)}")

		WinWaitActive("[TITLE:Swifty Xena Pro]", "", 10)
		ControlClick("[TITLE:Swifty Xena Pro]", "", "[CLASS:TButton; TEXT:&Extract Files...]")
		WinWaitActive("[TITLE:Open]", "", 10)

		Sleep(200)
		Send("c:\\out\\${path.basename(r.inPath)}{ENTER}")
		Sleep(200)

		WinWaitActive("[CLASS:TMessageForm; TITLE:Swifty Xena Pro]", "", 10)
		ControlClick("[CLASS:TMessageForm; TITLE:Swifty Xena Pro]", "", "[CLASS:TButton; TEXT:OK]")
		
		WinClose("[TITLE:Swifty Xena Pro]")
		
		FileDelete("c:\\out\\${path.basename(r.inPath)}")`
});
