import {Format} from "../../Format.js";

export class webmVideo extends Format
{
	name         = "WEBM Video";
	website      = "http://fileformats.archiveteam.org/wiki/WebM";
	ext          = [".webm"];
	magic        = ["WebM", "EBML file, creator webm", "WebM video", "EBML file, WebM", "video/webm", "video/webmVideo", /^fmt\/573( |$)/];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg"];
}
