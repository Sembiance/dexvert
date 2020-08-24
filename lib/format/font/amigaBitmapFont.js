"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	fileUtil = require("@sembiance/xutil").file,
	path = require("path");

exports.meta =
{
	name    : "Amiga Bitmap Font",
	website : "http://fileformats.archiveteam.org/wiki/Amiga_bitmap_font",
	ext     : [".font"],
	magic   : ["Amiga bitmap Font", "AmigaOS bitmap font"],
	notes   : "Fony (Win32/wine) (see sandbox/app/) is supposed to be able to open these, but I wasn't able to use it"
};

exports.steps =
[
	(state, p) => p.util.wine.run({cmd : "Fony.exe", args : [state.input.base], cwd : state.input.dirPath, autoItScript : `
		WinActivate("[CLASS:TMain_Form]", "")
		Sleep(1000)
		Send("!f")
		Sleep(500)
		Send("e")
		Sleep(500)
		Send("{DOWN}")
		Sleep(500)
		Send("{ENTER}")
		Sleep(500)
		Send("{ENTER}")
		Sleep(1000)
		Send("{ENTER}")
		Sleep(1000)
		Send("!f")
		Sleep(500)
		Send("x")`, preWineCleanup : (wineDirPath, cb) =>
	{
		tiptoe(
			function findBDF()
			{
				fileUtil.glob(path.join(wineDirPath, "drive_c", "users", "sembiance", "Desktop"), "*.bdf", this);
			},
			function moveBDF(bdfFilePaths)
			{
				if(!bdfFilePaths || bdfFilePaths.length===0 || !fileUtil.existsSync(bdfFilePaths[0]))
					return this();
				
				fileUtil.move(bdfFilePaths[0], path.join(state.cwd, "outfile.bdf"), this);
			},
			function convertBDFToPCF()
			{
				p.util.program.run("bdftopcf", {args : p.program.bdftopcf.args(state, p, path.join(state.cwd, "outfile.bdf"))})(state, p, this);
			},
			cb
		);
	}})
];
