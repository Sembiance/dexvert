import {Format} from "../../Format.js";

export class wma extends Format
{
	name             = "Windows Media Audio";
	website          = "http://fileformats.archiveteam.org/wiki/WMA";
	ext              = [".wma", ".asf"];
	magic            = ["Windows Media (generic)", "Microsoft ASF", "Advanced Streaming Format (generic)", "application/vnd.ms-asf", /^fmt\/132( |$)/];
	confidenceAdjust = () => -10;	// Reduce by 10 so that wmv matches first
	metaProvider     = ["ffprobe"];
	converters       = ["ffmpeg[outType:mp3]"];
}
