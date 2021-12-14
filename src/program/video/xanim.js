import {xu} from "xu";
import {Program} from "../../Program.js";

export class xanim extends Program
{
	website = "https://github.com/Sembiance/xanim";
	package = "media-video/xanim";
	unsafe  = true;
	notes   = "The dexvert version of xanim has special export functionality, originally based on the loki xanim fork, but I've ehnhanced it to support other animation formats and output correctly on 32bit x11 displays";
	flags   = {
		frameDelay : "Duration of delay between animation frames. Default: 10"
	};
	bin  = "xanim";
	args = r => ["+Ze", "+l0", "-Zr", "+Ee", r.inFile()];
	cwd  = r => r.outDir();

	// xanim plays back in real time, so if the video is longer than 5 minutes, it just will get truncated
	runOptions = ({virtualX : true, timeout : xu.MINUTE*5});
	chain      = r => `*joinAsGIF[frameDelay:${r.flags.frameDelay || 10}] -> ffmpeg`;
	renameOut  = false;
}


/*
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
*/
