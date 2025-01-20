import {Format} from "../../Format.js";

export class ipuRawVideo extends Format
{
	name         = "Raw IPU Video";
	ext          = [".ipu"];
	magic        = ["raw IPU Video (ipu)"];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg[format:ipu]"];
}
