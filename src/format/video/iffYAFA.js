import {Format} from "../../Format.js";

export class iffYAFA extends Format
{
	name       = "IFF YAFA Animation";
	website    = "http://fileformats.archiveteam.org/wiki/YAFA";
	mimeType   = "video/x-yafa";
	ext        = [".yafa"];
	magic      = ["IFF data, YAFA animation", "YAFA Animation"];

	// ffmpeg doesn't support decoding animated webp yet, so I can't go directly from abydos to ffmpeg: https://trac.ffmpeg.org/ticket/4907
	converters = [`abydosconvert[format:${this.mimeType}] -> convert[outType:gif] -> ffmpeg`];
}
