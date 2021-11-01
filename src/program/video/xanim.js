"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	fileUtil = require("@sembiance/xutil").file,
	tiptoe = require("tiptoe");

exports.meta =
{
	website       : "https://github.com/Sembiance/xanim",
	gentooPackage : "media-video/xanim",
	gentooOverlay : "dexvert",
	unsafe        : true,
	notes         : "The dexvert version of xanim has special export functionality, originally based on the loki xanim fork, but I've ehnhanced it to support other animation formats and output correctly on 32bit x11 displays",
	flags         :
	{
		xanimDelay : "Duration of delay between animation frames. Default: 10"
	}
};

exports.bin = () => "xanim";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, `${state.input.name}.mp4`)) => { r.outPath = outPath; return ["+Ze", "+l0", "-Zr", "+Ee", inPath]; };

// xanim plays back in real time, so if the video is longer than 4 minutes, it just will get truncated
exports.runOptions = () => ({virtualX : true, timeout : XU.MINUTE*4});

exports.post = (state, p, r, cb) =>
{
	tiptoe(
		function findOutputFrames()
		{
			fileUtil.glob(state.cwd, "xanimf*.ppm", {nodir : true}, this);
		},
		function generateAnimatedGIF(frameFilePaths=[])
		{
			if(!frameFilePaths.length)
				return this.finish();

			this.data.GIFFilePath = fileUtil.generateTempFilePath(state.cwd, ".gif");
			const convertArgs = ["-delay", `${r.flags.xanimDelay || 10}`, "-loop", "0", "-dispose", "previous"];
			convertArgs.push(...frameFilePaths, ...p.util.program.args(state, p, "convert").slice(1, -1), this.data.GIFFilePath);
			p.util.program.run("convert", {args : convertArgs})(state, p, this);
		},
		function convertToMP4()
		{
			p.util.program.run("ffmpeg", {flags : {ffmpegExt : ".mp4"}, argsd : [this.data.GIFFilePath, r.outPath]})(state, p, this);
		},
		cb
	);
};
