import {Format} from "../../Format.js";

export class mp4 extends Format
{
	name         = "MPEG4 Video";
	website      = "http://fileformats.archiveteam.org/wiki/MP4";
	ext          = [".mp4", ".m4v"];
	mimeType     = "video/mp4";
	magic        = [/MP4 Base Media/, "MPEG-4 Media File", /^ISO Media.*M4V/, "ISO Media, MP4"];
	untouched    = true;
	metaProvider = ["mplayer"];
}
