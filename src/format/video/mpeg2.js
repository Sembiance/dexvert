import {Format} from "../../Format.js";

export class mpeg2 extends Format
{
	name         = "MPEG-2";
	website      = "http://fileformats.archiveteam.org/wiki/MPEG-2";
	ext          = [".mpg", ".mp2", ".mpeg", ".m2v"];
	mimeType     = "video/mpeg";
	magic        = ["MPEG-2 Elementary Stream", "MPEG-2 Program Stream", "MPEG sequence, v2"];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg", "xanim"];
}
