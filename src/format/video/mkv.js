import {Format} from "../../Format.js";

export class mkv extends Format
{
	name         = "Matroska Video";
	website      = "http://fileformats.archiveteam.org/wiki/MKV";
	ext          = [".mkv"];
	priority     = this.PRIORITY.LOW;
	magic        = ["Matroska Video stream", "Matroska data", "EBML file, creator matroska", "Extensible Binary Meta Language / Matroska stream", "EBML file, Matroska data", "application/x-matroska", /^fmt\/569( |$)/];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg"];
}
