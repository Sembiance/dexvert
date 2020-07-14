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
	if(state.id.family==="image")
	{
		state.ffmpegExt = ".png";
		return ["-i", state.input.filePath, "-frames:v", "1", path.join(state.output.dirPath, "outfile" + state.unoconvExt)];
	}

	// Assume video
	state.ffmpegExt = ".mp4";
	return ["-i", state.input.filePath, "-c:v", "libx264rgb", "-crf", "0", "-preset", "ultrafast", path.join(state.output.dirPath, "outfile" + state.unoconvExt)];
};

exports.post = (state, p, cb) => p.util.file.move(path.join(state.output.absolute, "outfile" + state.ffmpegExt), path.join(state.output.absolute, state.input.name + state.ffmpegExt))(state, p, cb);
