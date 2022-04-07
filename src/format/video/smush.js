import {Format} from "../../Format.js";

export class smush extends Format
{
	name         = "LucasArts SMUSH Video";
	website      = "https://wiki.multimedia.cx/index.php/Smush";
	ext          = [".nut", ".san"];
	magic        = ["LucasArts Smush Animation Format", "Smush Animation format"];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg"];
}
