import {Format} from "../../Format.js";

export class oggTheoraVideo extends Format
{
	name         = "Ogg Theora Video";
	website      = "http://fileformats.archiveteam.org/wiki/Theora";
	ext          = [".ogg", ".ogv"];
	magic        = ["Ogg data, Theora video", "Ogg Theora video"];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg"];
}
