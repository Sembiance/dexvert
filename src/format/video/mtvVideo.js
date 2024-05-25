import {Format} from "../../Format.js";

export class mtvVideo extends Format
{
	name         = "MTV Video";
	website      = "http://fileformats.archiveteam.org/wiki/MTV_Video_(.AMV)";
	ext          = [".amv"];
	magic        = ["RIFF (little-endian) data, AMV", "MTV Movie", "RIFF Datei: unbekannter Typ 'AMV '"];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg"];
}
