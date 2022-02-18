import {Format} from "../../Format.js";

export class wma extends Format
{
	name         = "Windows Media Audio";
	ext          = [".wma"];
	magic        = ["Windows Media (generic)", "Microsoft ASF", "Advanced Streaming Format (generic)"];
	metaProvider = ["ffprobe"];
	converters   = ["ffmpeg[outType:mp3]"];
}
