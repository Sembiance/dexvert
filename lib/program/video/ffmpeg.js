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
exports.args = state =>
{
	const ffmpegArgs = [];

	// Can run `ffmpeg -formats` for a list
	if(state.ffmpegFormat)
		ffmpegArgs.push("-f", state.ffmpegFormat);

	if(state.id.family==="image")
	{
		state.ffmpegExt = ".png";
		ffmpegArgs.push("-i", state.input.filePath, "-frames:v", "1", path.join(state.output.dirPath, `outfile${state.ffmpegExt}`));
	}
	else if(state.id.family==="audio")
	{
		state.ffmpegExt = ".flac";
		ffmpegArgs.push("-i", state.input.filePath, "-c:a", "flac", "-compression_level", "12", path.join(state.output.dirPath, `outfile${state.ffmpegExt}`));
	}
	else
	{
		state.ffmpegExt = ".mp4";

		// Browser friendly args:
		// I removed args ["-pix_fmt", "yuv420p"] because it would fail to convert some input videos when specified
		ffmpegArgs.push("-i", state.input.filePath, "-c:v", "libx264", "-crf", "1", "-preset", "slow", path.join(state.output.dirPath, `outfile${state.ffmpegExt}`));

		// Pixel Perfect args:
		//ffmpegArgs.push("-i", state.input.filePath, "-c:v", "libx264rgb", "-crf", "0", "-preset", "ultrafast", path.join(state.output.dirPath, `outfile${state.ffmpegExt}`));
	}

	return ffmpegArgs;
};

exports.post = (state, p, cb) => p.util.file.move(path.join(state.output.absolute, `outfile${state.ffmpegExt || ".mp4"}`), path.join(state.output.absolute, state.input.name + (state.ffmpegExt || ".mp4")))(state, p, cb);
