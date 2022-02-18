import {Format} from "../../Format.js";

export class wmv extends Format
{
	name         = "Windows Media Video";
	ext          = [".wmv"];
	magic        = ["Windows Media (generic)", "Microsoft ASF", "Advanced Streaming Format (generic)"];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg"];
}
