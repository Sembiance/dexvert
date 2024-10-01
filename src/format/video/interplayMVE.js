import {Format} from "../../Format.js";

export class interplayMVE extends Format
{
	name         = "Interplay MVE Video";
	website      = "https://wiki.multimedia.cx/index.php/Interplay_MVE";
	ext          = [".mve"];
	magic        = ["Interplay MVE video", "Interplay MVE Movie", "Interplay MVE (ipmovie)"];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg[format:ipmovie]"];
}
