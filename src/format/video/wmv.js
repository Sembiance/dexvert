import {Format} from "../../Format.js";

export class wmv extends Format
{
	name         = "Windows Media Video";
	website      = "http://fileformats.archiveteam.org/wiki/WMV";
	ext          = [".wmv", ".asf", ".xesc"];
	magic        = ["Windows Media (generic)", "Microsoft ASF", "Advanced Streaming Format (generic)", "Windows Media-Audio/Video Datei (WMA/WMV)", /^fmt\/(131|132|133)( |$)/];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg", "mencoderWinXP"];
}
