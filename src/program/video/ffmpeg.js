import {Program} from "../../Program.js";

export class ffmpeg extends Program
{
	website = "https://ffmpeg.org/";
	package = "media-video/ffmpeg";
	flags   = {
		outType     : `Which format to output: png mp3 mp4 flac. Default is mp4`,
		format      : "Specify which format to treat the input file as. Run `ffmpeg -formats` for a list. Default: Let ffmpeg decide",
		codec       : "Specify which codec to treat the input file as. Run `ffmpeg -codecs` for a list. Default: Let ffmpeg decide",
		fps         : "What frame rate to specify for conversion. Default: Let ffmpeg decide",
		rate        : "What rate to set for the output. Default: Let ffmpeg decide",
		maxDuration : "Maximum duration (in seconds) to allow the output file to be"
	};
	bin = "ffmpeg";
	args = async r =>
	{
		const a = [];
		if(r.flags.format)
			a.push("-f", r.flags.format);
		if(r.flags.codec)
			a.push("-c", r.flags.codec);
		if(r.flags.fps)
			a.push("-r", r.flags.fps);
		if(r.flags.maxDuration)
			a.push("-t", r.flags.maxDuration);

		switch(r.flags.outType || "mp4")
		{
			case "png":
				a.push("-i", r.inFile(), "-frames:v", "1", await r.outFile("out.png"));
				break;

			case "wav":
				a.push("-i", r.inFile());
				if(r.flags.rate)
					a.push("-af", `asetrate=${r.flags.rate}`);
				a.push("-c:a", "pcm_u8", await r.outFile("out.wav"));
				break;

			case "mp3":
				a.push("-i", r.inFile());
				if(r.flags.rate)
					a.push("-af", `asetrate=${r.flags.rate}`);
				a.push("-c:a", "libmp3lame", "-qscale:a", "0", await r.outFile("out.mp3"));
				break;

			case "flac":
				a.push("-i", r.inFile(), "-c:a", "flac", "-compression_level", "12", await r.outFile("out.flac"));
				break;
			
			case "gif":
				a.push("-i", r.inFile(), await r.outFile("out.gif"));
				break;

			default:
				// OK. So the `-pix_fmt yuv420p` is REQUIRED for iOS devices to actually play these videos.
				// This then requires that the video WxH be divisible by 2, thus the 'pad' video filter
				// Also, this pixel format reduces quality and there isn't anything I can do about it. See the info here: https://awk.space/blog/pixel-perfect-webm/
				// For PIXEL PERFECT conversion, I would use these args: ffmpegArgs.push("-i", inPath, "-c:v", "libx264rgb", "-crf", "0", "-preset", "ultrafast", outPath);
				// Sadly that's not supported in most browsers. Sigh. I really don't want to support multiple video formats, for different devices, so I just choose the most compatible and live with the compression artifacts and decrease in quality.
				a.push("-i", r.inFile(), "-c:v", "libx264", "-vf", "pad='width=ceil(iw/2)*2:height=ceil(ih/2)*2'", "-crf", "15", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "faststart", await r.outFile("out.mp4"));
		}
		return a;
	};
}
