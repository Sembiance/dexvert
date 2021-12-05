/*
import {Program} from "../../Program.js";

export class ffdec extends Program
{
	website = "https://github.com/jindrapetrik/jpexs-decompiler";
	package = "media-gfx/ffdec";
	flags = {"ffdecKeepAsGIF":"Leave the animation as a GIF, don't convert to MP4","ffdecMaxFrames":"Maximum number of frames to extract. Default: 500"};
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	runUtil = require("@sembiance/xutil").run,
	path = require("path"),
	tiptoe = require("tiptoe");

exports.meta =
{
	website       : "https://github.com/jindrapetrik/jpexs-decompiler",
	package : "media-gfx/ffdec",
	flags :
	{
		ffdecKeepAsGIF : "Leave the animation as a GIF, don't convert to MP4",
		ffdecMaxFrames : "Maximum number of frames to extract. Default: 500"
	}
};

exports.bin = () => "ffdec";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=state.output.dirPath) => ([
	"-cli",
	"-config", "loopMedia=false,parallelSpeedUpThreadCount=20",
	"-exportTimeout", "120",	// Limit export time to 2 minutes. Any longer is likely due to tons of 'dynamic' shapes or large individual frames, don't need to extract all that stuff
	"-select", `1-${r.flags.ffdecMaxFrames || 500}`,
	"-export", "script,image,shape,morphshape,movie,font,frame,button,sound,binaryData,text", outPath, inPath]);	// Don't extract sprite because it's just generated from shapes/images and can be thousands of them

exports.post = (state, p, r, cb) =>
{
	const framesDirPath = path.join(state.output.absolute, "frames");

	tiptoe(
		function findFrames()
		{
			fileUtil.glob(framesDirPath, "*.png", {nodir : true}, this.parallel());

			// ffdec leaves empty directories if it times out, so delete those
			runUtil.run("find", [state.output.absolute, "-type", "d", "-empty", "-delete"], {silent : true, "ignore-stderr" : true}, this.parallel());
		},
		function getFrameRate(frameFilePaths)
		{
			if(frameFilePaths.length<=1)
				return this.finish();

			this.data.frameFilePaths = frameFilePaths.multiSort([frameFilePath => path.basename(frameFilePath, ".ext").padStart(10, "0")]);
			runUtil.run("swfdump", ["--rate", r.args.last()], {silent : true, cwd : state.cwd}, this);
		},
		function joinFrames(frameRateRaw)
		{
			const frameDelay = (100/(+frameRateRaw.match(/-r (?<rate>\d.+)/)?.groups?.rate));
			this.data.GIFFilePath = path.join(state.output.absolute, `${state.input.name}.gif`);
			p.util.program.run("convert", {args : ["-delay", frameDelay.toString(), "-loop", "0", "-dispose", "previous", ...this.data.frameFilePaths, ...p.util.program.args(state, p, "convert").slice(1, -1), this.data.GIFFilePath]})(state, p, this);
		},
		function convertToMP4()
		{
			fileUtil.unlink(framesDirPath, this.parallel());

			if(!r.flags.ffdecKeepAsGIF)
				p.util.program.run("ffmpeg", {flags : {ffmpegExt : ".mp4"}, argsd : [this.data.GIFFilePath]})(state, p, this.parallel());
		},
		function removeSourceGIF()
		{
			if(r.flags.ffdecKeepAsGIF)
				this();
			else
				fileUtil.unlink(this.data.GIFFilePath, this);
		},
		cb
	);
};
*/
