import {Format} from "../../Format.js";

export class webmVideo extends Format
{
	name         = "WEBM Video";
	website      = "http://fileformats.archiveteam.org/wiki/Webm";
	ext          = [".mkv"];
	magic        = ["WebM", "Matroska data", "EBML file, creator webm", "WebM video"];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg"];
}
