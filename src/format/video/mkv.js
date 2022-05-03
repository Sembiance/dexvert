import {Format} from "../../Format.js";

export class mkv extends Format
{
	name         = "Matroska Video";
	website      = "http://fileformats.archiveteam.org/wiki/MKV";
	ext          = [".mkv"];
	magic        = ["Matroska Video stream", "Matroska data", "EBML file, creator matroska", "Extensible Binary Meta Language / Matroska stream"];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg"];
}
