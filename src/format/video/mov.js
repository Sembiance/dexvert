import {Format} from "../../Format.js";

export class mov extends Format
{
	name         = "Apple QuickTime movie";
	website      = "http://fileformats.archiveteam.org/wiki/MOV";
	ext          = [".mov", ".omv", ".pmv"];
	mimeType     = "video/quicktime";
	magic        = ["Apple QuickTime movie", "QuickTime Movie", "Mac QuickTime video", /^MacBinary II.+'MooV'/];
	trustMagic   = true;
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg", "xanim", "qt_flatt", "mencoderWinXP"];
}
