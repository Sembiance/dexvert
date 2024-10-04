import {Format} from "../../Format.js";

export class rl2Video extends Format
{
	name         = "RL2 Video";
	website      = "https://wiki.multimedia.cx/index.php/RL2";
	ext          = [".rl2"];
	magic        = ["RL2 (rl2)"];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg[format:rl2]"];
}
