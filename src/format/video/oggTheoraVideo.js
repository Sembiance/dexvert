import {Format} from "../../Format.js";

export class oggTheoraVideo extends Format
{
	name         = "Ogg Theora Video";
	website      = "http://fileformats.archiveteam.org/wiki/Theora";
	ext          = [".ogg", ".ogv"];
	magic        = ["Ogg data, Theora video", "Ogg Theora video", "video/x-theora+ogg", "application/ogg", "Ogg Vorbis Skeleton/Video", "deark: ogg (Ogg Theora+Vorbis)", /^Ogg data, Skeleton/, /^fmt\/(944|945)( |$)/];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg"];
}
