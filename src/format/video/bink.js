import {Format} from "../../Format.js";

export class bink extends Format
{
	name         = "Bink Video";
	website      = "http://fileformats.archiveteam.org/wiki/Bink_Video";
	ext          = [".bik", ".bik2", ".bk2"];
	magic        = [/^Bink2? [Vv]ideo/, /^fmt\/731( |$)/];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg"];
}
