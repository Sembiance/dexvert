import {Format} from "../../Format.js";

export class mov extends Format
{
	name         = "Apple QuickTime movie";
	website      = "http://fileformats.archiveteam.org/wiki/MOV";
	ext          = [".mov"];
	mimeType     = "video/quicktime";
	magic        = ["Apple QuickTime movie", "QuickTime Movie"];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg", "xanim"];
}
