import {Format} from "../../Format.js";

export class mp4 extends Format
{
	name             = "MPEG4 Video";
	website          = "http://fileformats.archiveteam.org/wiki/MP4";
	ext              = [".mp4", ".m4v", ".f4v"];
	mimeType         = "video/mp4";
	magic            = [
		// generic
		/MP4 Base Media/, "MPEG-4 Media File", /^ISO Media.*M4V/, "ISO Media, MP4", "video/mp4", "ISO Media, MPEG v4 system", "MP4 v2 container video", "iTunes Video",
		/^Format: MP4 Video\[.*mp4[12]/, /^Format: MP4 Video\[isom/, /^ISO Media, MPEG-4 \(\.MP4\)/, /^Format: MP4 Video$/,
		/^fmt\/199( |$)/,
		
		// specific
		"iTunes Apple TV Video"
	];
	idMeta           = ({macFileType, macFileCreator}) => (macFileType==="mpg4" && macFileCreator==="TVOD") || macFileType==="M4V ";
	confidenceAdjust = () => -10; // Adjust confidence so other MP4 container video-like formats (audio/threeGAudio match first)
	untouched        = true;
	metaProvider     = ["mplayer"];
}
