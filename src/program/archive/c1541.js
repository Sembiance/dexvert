"use strict";
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	fs = require("fs"),
	tiptoe = require("tiptoe"),
	path = require("path");

exports.meta =
{
	website        : "https://vice-emu.sourceforge.io/",
	gentooPackage  : "app-emulation/vice",
	gentooUseFlags : "alsa ffmpeg ipv6 nls png sdl sdlsound threads zlib"
};

exports.bin = () => "c1541";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=state.output.dirPath) =>
{
	r.argsInPathAbsolute = path.resolve(state.cwd, inPath);
	r.argsOutPathAbsolute = path.resolve(state.cwd, outPath);
	
	return [];
};
exports.runOptions = (state, p, r) => ({"ignore-stderr" : true, cwd : r.argsOutPathAbsolute, inputData : `attach "${r.argsInPathAbsolute}"\nextract\nquit\n`});

exports.post = (state, p, r, cb) =>
{
	tiptoe(
		function findOutputFiles()
		{
			fileUtil.glob(state.output.absolute, "**", {nodir : true}, this);
		},
		function renameExtensions(filePaths)
		{
			filePaths.parallelForEach((filePath, subcb) =>
			{
				let newFilePath = filePath;

				// Often the extension is leading the filename, such as rpm.still.life
				// So we check to see if we have a 1 to 3 character extensions at the start of the file and if so, we move it to the end instead
				// This is done because some file formats (such as runPaint) rely on a proper extension
				const parts = (path.basename(newFilePath).match(/^(?<ext>\w{1,3}\.).+$/) || {groups : {}}).groups;
				if(parts.ext)
					newFilePath = path.join(path.dirname(newFilePath), `${path.basename(newFilePath).substring(parts.ext.length)}.${parts.ext.slice(0, -1)}`);

				if(newFilePath!==filePath)
					fs.rename(filePath, newFilePath, subcb);
				else
					setImmediate(subcb);
			}, this);
		},
		cb
	);
};
