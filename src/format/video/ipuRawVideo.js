import {Format} from "../../Format.js";

export class ipuRawVideo extends Format
{
	name         = "Raw IPU Video";
	ext          = [".ipu"];
	magic        = ["raw IPU Video (ipu)"];
	metaProvider = ["ffprobe"];
	converters   = ["ffmpeg[format:ipu]"];
}
