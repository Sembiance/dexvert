"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://ffmpeg.org/",
	gentooPackage : "media-video/ffmpeg",
	gentooUseFlags : "X alsa amr bzip2 encode fontconfig gpl iconv jpeg2k lzma mp3 network opengl openssl opus postproc svg theora threads truetype v4l vaapi vdpau vorbis vpx webp x264 xvid zlib"
};

exports.bin = () => "ffmpeg";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, `outfile${r.flags.ffmpegExt || (state.id.family==="image" ? ".png" : (state.id.family==="audio" ? ".mp3" : ".mp4"))}`)) =>
{
	const ffmpegArgs = [];

	// Can run `ffmpeg -formats` for a list
	r.flags.ffmpegExt = r.flags.ffmpegExt || (state.id.family==="image" ? ".png" : (state.id.family==="audio" ? ".mp3" : ".mp4"));
	if(r.flags.ffmpegFormat)
		ffmpegArgs.push("-f", r.flags.ffmpegFormat);

	if(r.flags.ffmpegExt===".png")
		ffmpegArgs.push("-i", inPath, "-frames:v", "1", outPath);
	else if(r.flags.ffmpegExt===".mp3")
		ffmpegArgs.push("-i", inPath, "-c:a", "libmp3lame", "-qscale:a", "0", outPath);
	else if(r.flags.ffmpegExt===".flac")
		ffmpegArgs.push("-i", inPath, "-c:a", "flac", "-compression_level", "12", outPath);
	else
		ffmpegArgs.push("-i", inPath, "-c:v", "libx264", "-crf", "1", "-preset", "slow", outPath);	// Browser friendly args. I removed args ["-pix_fmt", "yuv420p"] because it would fail to convert some input videos when specified

	// Pixel Perfect args:
	//ffmpegArgs.push("-i", inPath, "-c:v", "libx264rgb", "-crf", "0", "-preset", "ultrafast", outPath);

	return ffmpegArgs;
};

exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, `outfile${r.flags.ffmpegExt}`), path.join(state.output.absolute, state.input.name + r.flags.ffmpegExt))(state, p, cb);
