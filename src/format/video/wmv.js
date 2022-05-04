import {Format} from "../../Format.js";

export class wmv extends Format
{
	name         = "Windows Media Video";
	ext          = [".wmv", ".asf", ".xesc"];
	magic        = ["Windows Media (generic)", "Microsoft ASF", "Advanced Streaming Format (generic)", "fmt/131", "fmt/132", "fmt/133"];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg", "mencoderWinXP"];
}
