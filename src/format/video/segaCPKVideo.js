import {Format} from "../../Format.js";

export class segaCPKVideo extends Format
{
	name         = "Sega CPK video";
	website      = "https://wiki.multimedia.cx/index.php/JV";
	ext          = [".cpk", ".cak", ".film"];
	magic        = ["Sega CPK video", "Sega FILM / CPK (film_cpk)"];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg[format:film_cpk]"];
}
