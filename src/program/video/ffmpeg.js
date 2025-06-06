import {Program} from "../../Program.js";
import {fileUtil, imageUtil} from "xutil";

export class ffmpeg extends Program
{
	website = "https://ffmpeg.org/";
	package = "media-video/ffmpeg";
	flags   = {
		format      : "Specify which format to treat the input file as. Run `ffmpeg -formats` for a list. Default: Let ffmpeg decide",
		outType     : `Which format to output: png mp3 mp4 flac. WARNING! If input is a .wav, best to send through sox first, because ffmpeg can't handle anything except perfect WAV files. Default is mp4`,
		codec       : "Specify which codec to treat the input file as. Run `ffmpeg -codecs` for a list. Default: Let ffmpeg decide",
		fps         : "What frame rate to specify for conversion. Default: Let ffmpeg decide",
		rate        : "What rate to set for the output. Default: Let ffmpeg decide",
		numStreams  : "Total number of sterams available",
		streamNum   : "Which stream num to extract. Default: Let ffmpeg decide",
		maxDuration : "Maximum duration (in seconds) to allow the output file to be",
		libre       : "Use librempeg instead of ffmpeg"
	};
	bruteFlags = { archive : {}, audio : { outType : "mp3" }, image : { outType : "png" }, music : { outType : "mp3" } };

	bin  = r => (r.flags.libre ? "librempeg" : "ffmpeg");
	args = async r =>
	{
		const inFileArgs = [];
		const inFilePaths = r.inFiles({absolute : true});
		
		if(inFilePaths.length>1)
		{
			r.imagesListFilePath = await fileUtil.genTempPath(undefined, ".txt");
			inFileArgs.push("-i", r.imagesListFilePath);

			for(const inFilePath of inFilePaths)
				await fileUtil.writeTextFile(r.imagesListFilePath, `file '${inFilePath}'\n`, {append : true, create : true});
		}
		else
		{
			inFileArgs.push("-i", `file:${r.inFile()}`);	// without the file: prefix, if the filename contains a colon, ffmpeg will get confused
		}

		const noMeta = ["-bitexact", "-fflags", "+bitexact", "-flags:v", "+bitexact", "-flags:a", "+bitexact"];
		const a = ["-y"];
		if(r.flags.format)
			a.push("-f", r.flags.format);
		if(r.flags.codec)
			a.push("-c", r.flags.codec);
		if(r.flags.fps)
			a.push("-r", r.flags.fps);
		if(r.flags.maxDuration)
			a.push("-t", r.flags.maxDuration);
		if(inFilePaths.length>1)
			a.push("-f", "concat", "-safe", "0");

		switch(r.flags.outType || "mp4")
		{
			case "png":
				a.push(...inFileArgs, "-frames:v", "1", ...noMeta, `file:${await r.outFile("out.png")}`);
				break;

			case "wav":
				a.push(...inFileArgs);
				if(r.flags.streamNum)
					a.push("-map", `0:a:${r.flags.streamNum}`);
				if(r.flags.rate)
					a.push("-af", `asetrate=${r.flags.rate}`);
				a.push("-c:a", "pcm_u8", ...noMeta, await r.outFile("out.wav"));
				break;

			case "mp3":
				a.push(...inFileArgs);
				if(r.flags.streamNum)
					a.push("-map", `0:a:${r.flags.streamNum}`);
				if(r.flags.rate)
					a.push("-af", `asetrate=${r.flags.rate}`);
				a.push("-c:a", "libmp3lame", "-b:a", "192k", ...noMeta, await r.outFile("out.mp3"));
				break;

			case "flac":
				a.push(...inFileArgs);
				if(r.flags.streamNum)
					a.push("-map", `0:a:${r.flags.streamNum}`);
				a.push("-c:a", "flac", "-compression_level", "12", ...noMeta, await r.outFile("out.flac"));
				break;
			
			case "gif":
				a.push(...inFileArgs, ...noMeta, await r.outFile("out.gif"));
				break;

			default:
				// OK. So the `-pix_fmt yuv420p` is REQUIRED for iOS devices to actually play these videos.
				// This then requires that the video WxH be divisible by 2, thus the 'pad' video filter
				// Also, this pixel format reduces quality and there isn't anything I can do about it. See the info here: https://awk.space/blog/pixel-perfect-webm/
				// For PIXEL PERFECT conversion, I would use these args: ffmpegArgs.push(...inFileArgs, "-c:v", "libx264rgb", "-crf", "0", "-preset", "ultrafast", outPath);
				// Sadly that's not supported in most browsers. Sigh. I really don't want to support multiple video formats, for different devices, so I just choose the most compatible and live with the compression artifacts and decrease in quality.
				a.push(...inFileArgs, "-c:v", "libx264", "-vf", "pad='width=ceil(iw/2)*2:height=ceil(ih/2)*2'", "-crf", "15", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "faststart");
				
				if(inFilePaths.length>1)
				{
					const [w, h] = await imageUtil.getWidthHeight(inFilePaths[0]);
					a.push("-aspect", `${w}:${h}`);
				}

				a.push(...noMeta, await r.outFile("out.mp4"));
		}

		return a;
	};

	post = async r =>
	{
		if(r.imagesListFilePath)
			await fileUtil.unlink(r.imagesListFilePath, {recursive : true});
	};

	renameOut = {
		alwaysRename : true,
		renamer      : [({r, newName, newExt}) => (Object.hasOwn(r.flags, "streamNum") ? [newName, r.flags.streamNum.toString().padStart(r.flags.numStreams.toString().length, "0"), newExt] : [newName, newExt])]
	};
}
