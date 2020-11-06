"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	fileUtil = require("@sembiance/xutil").file,
	path = require("path");

exports.meta =
{
	website : "http://hukka.ncn.fi/?fony"
};

exports.wine = () => "Fony.exe";
exports.args = (state, p, r, inPath=state.input.base) => ([inPath]);
exports.cwd = state => state.input.dirPath;

exports.wineOptions = (state, p) => ({
	autoItScript : `
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
		Send("x")`,
	preWineCleanup : (wineDirPath, cb) =>
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
				
				p.util.program.run("bdftopcf", {argsd : [bdfFilePaths[0]]})(state, p, this);
			},
			cb
		);
	}
});

exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.cwd, "out.txt"), path.join(state.output.absolute, `${state.input.name}.txt`))(state, p, cb);
