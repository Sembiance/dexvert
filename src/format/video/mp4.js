import {Format} from "../../Format.js";

export class mp4 extends Format
{
	name             = "MPEG4 Video";
	website          = "http://fileformats.archiveteam.org/wiki/MP4";
	ext              = [".mp4", ".m4v", ".f4v"];
	mimeType         = "video/mp4";
	magic            = [/MP4 Base Media/, "MPEG-4 Media File", /^ISO Media.*M4V/, "ISO Media, MP4", "video/mp4", "ISO Media, MPEG v4 system", "MP4 v2 container video", /^Format: MP4 Video\[.*mp4[12]/, /^fmt\/199( |$)/];
	confidenceAdjust = () => -10; // Adjust confidence so other MP4 container video-like formats (audio/threeGAudio match first)
	untouched        = true;
	metaProvider     = ["mplayer"];
}
