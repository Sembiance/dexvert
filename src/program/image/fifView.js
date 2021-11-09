/*
import {Program} from "../../Program.js";

export class fifView extends Program
{
	website = "http://cd.textfiles.com/wthreepack/wthreepack-1/COMPRESS/FIFDEMO.ZIP";
	unsafe = true;
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	tiptoe = require("tiptoe"),
	fileUtil = require("@sembiance/xutil").file,
	runUtil = require("@sembiance/xutil").run;

exports.meta =
{
	website : "http://cd.textfiles.com/wthreepack/wthreepack-1/COMPRESS/FIFDEMO.ZIP",
	unsafe  : true
};

exports.qemu = () => "c:\\dexvert\\FIFView\\FIFView.exe";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);

exports.qemuData = (state, p, r) => ({
	osid         : "winxp",
	inFilePaths  : [r.args.last()],
	dontMaximize : true,
	script       : `
		#include <ScreenCapture.au3>

		WinWaitActive("[TITLE:Fractal Viewer Helper App; CLASS:DECO_NT_Class]", "", 10)
		Sleep(1000)

		_ScreenCapture_CaptureWnd("c:\\out\\out.bmp", WinGetHandle("[TITLE:Fractal Viewer Helper App; CLASS:DECO_NT_Class]"), 4, 42, 644, 441, False);

		Sleep(500)
		Send("!f")
		Sleep(100)
		Send("x")

		WinWaitClose("[TITLE:Fractal Viewer Helper App; CLASS:DECO_NT_Class]", "", 10)`
});

exports.post = (state, p, r, cb) =>
{
	tiptoe(
		function trimOutput()
		{
			runUtil.run("convert", [path.join(state.output.absolute, "out.bmp"), "-bordercolor", "#FFFFFF", "-border", "1x1", "-fuzz", "20%", "-trim", "+repage", path.join(state.output.absolute, `${state.input.name}.png`)], runUtil.SILENT, this);
		},
		function removeBMP()
		{
			fileUtil.unlink(path.join(state.output.absolute, "out.bmp"), this);
		},
		cb
	);
};
*/
