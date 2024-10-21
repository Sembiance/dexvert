import {Format} from "../../Format.js";

export class wmv extends Format
{
	name         = "Windows Media Video";
	website      = "http://fileformats.archiveteam.org/wiki/WMV";
	ext          = [".wmv", ".asf", ".xesc"];
	magic        = [
		// generic
		"Windows Media (generic)", "Microsoft ASF", "Advanced Streaming Format (generic)", "Windows Media-Audio/Video Datei (WMA/WMV)", "application/vnd.ms-asf", "ASF (Advanced / Active Streaming Format) (asf)", /^fmt\/(131|132|133|441)( |$)/,
		
		// specific
		"Microsoft Digital Video Recording"
	];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg", "mencoderWinXP"];
}
