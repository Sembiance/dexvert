import {Format} from "../../Format.js";

export class dreamForgeVideo extends Format
{
	name         = "DreamForge Video";
	website      = "https://wiki.multimedia.cx/index.php?title=DFA";
	ext          = [".dfa"];
	magic        = ["DreamForge video"];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg"];
}
