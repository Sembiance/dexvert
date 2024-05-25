import {Format} from "../../Format.js";

export class webmVideo extends Format
{
	name         = "WEBM Video";
	website      = "http://fileformats.archiveteam.org/wiki/WebM";
	ext          = [".mkv"];
	magic        = ["WebM", "EBML file, creator webm", "WebM video", /^fmt\/573( |$)/];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg"];
}
