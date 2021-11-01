"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website        : "https://ffmpeg.org/",
	gentooPackage  : "media-video/ffmpeg",
	gentooUseFlags : "X alsa amr bzip2 encode fontconfig gpl iconv jpeg2k lzma mp3 network opengl openssl opus postproc svg theora threads truetype v4l vaapi vdpau vorbis vpx webp x264 xvid zlib",
	flags          :
	{
		ffmpegExt         : `Which extension to convert into (".png", ".mp3", ".mp4", ".flac", etc). Default for image is .png, audio is .mp3 otherwise .mp4`,
		ffmpegFormat      : "Specify which format to treat the input file as. Run `ffmpeg -formats` for a list. Default: Let ffmpeg decide",
		ffmpegCodec       : "Specify which codec to treat the input file as. Run `ffmpeg -codecs` for a list. Default: Let ffmpeg decide",
		ffmpegFPS         : "What frame rate to specify for conversion. Default: Let ffmpeg decide",
		ffmpegRate        : "What rate to set for the output. Default: Let ffmpeg decide",
		ffmpegMaxDuration : "Maximum duration (in seconds) to allow the output file to be"
	}
};

exports.bin = () => "ffmpeg";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, `outfile${r.flags.ffmpegExt || (state.id.family==="image" ? ".png" : (state.id.family==="audio" ? ".mp3" : ".mp4"))}`)) =>
{
	const ffmpegArgs = [];

	// Can run `ffmpeg -formats` for a list
	r.flags.ffmpegExt = r.flags.ffmpegExt || (state.id.family==="image" ? ".png" : (state.id.family==="audio" ? ".mp3" : ".mp4"));
	if(r.flags.ffmpegFormat)
		ffmpegArgs.push("-f", r.flags.ffmpegFormat);
	if(r.flags.ffmpegCodec)
		ffmpegArgs.push("-c", r.flags.ffmpegCodec);
	if(r.flags.ffmpegFPS)
		ffmpegArgs.push("-r", r.flags.ffmpegFPS.toString());
	if(r.flags.ffmpegMaxDuration)
		ffmpegArgs.push("-t", r.flags.ffmpegMaxDuration.toString());

	switch (r.flags.ffmpegExt)
	{
		case ".png":
			ffmpegArgs.push("-i", inPath, "-frames:v", "1", outPath);
			break;

		case ".mp3":
		case ".wav":
			ffmpegArgs.push("-i", inPath);
			if(r.flags.ffmpegRate)
				ffmpegArgs.push("-af", `asetrate=${r.flags.ffmpegRate}`);
			
			if(r.flags.ffmpegExt===".mp3")
				ffmpegArgs.push("-c:a", "libmp3lame", "-qscale:a", "0");
			else if(r.flags.ffmpegExt===".wav")
				ffmpegArgs.push("-c:a", "pcm_u8");

			ffmpegArgs.push(outPath);
			break;

		case ".flac":
			ffmpegArgs.push("-i", inPath, "-c:a", "flac", "-compression_level", "12", outPath);
			break;
		
		case ".gif":
			ffmpegArgs.push("-i", inPath, outPath);
			break;

		default:
			ffmpegArgs.push("-i", inPath, "-c:v", "libx264", "-vf", "pad='width=ceil(iw/2)*2:height=ceil(ih/2)*2'", "-crf", "15", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "faststart", outPath);
	}

	// OK. So the `-pix_fmt yuv420p` is REQUIRED for iOS devices to actually play these videos.
	// This then requires that the video WxH be divisible by 2, thus the 'pad' video filter
	// Also, this pixel format reduces quality and there isn't anything I can do about it. See the info here: https://awk.space/blog/pixel-perfect-webm/
	// For PIXEL PERFECT conversion, I would use these args: ffmpegArgs.push("-i", inPath, "-c:v", "libx264rgb", "-crf", "0", "-preset", "ultrafast", outPath);
	// Sadly that's not supported in most browsers. Sigh. I really don't want to support multiple video formats, for different devices, so I just choose the most compatible and live with the comperssion and decrease in quality.

	return ffmpegArgs;
};

exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, `outfile${r.flags.ffmpegExt}`), path.join(state.output.absolute, state.input.name + r.flags.ffmpegExt))(state, p, cb);
