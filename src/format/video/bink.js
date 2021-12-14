import {Format} from "../../Format.js";

export class bink extends Format
{
	name         = "Bink Video";
	website      = "http://fileformats.archiveteam.org/wiki/Bink_Video";
	ext          = [".bik", ".bik2", ".bk2"];
	magic        = [/^Bink [Vv]ideo/];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg"];
}
