import {Format} from "../../Format.js";

export class dreamForgeVideo extends Format
{
	name         = "DreamForge Video";
	website      = "https://wiki.multimedia.cx/index.php/DFA";
	ext          = [".dfa"];
	magic        = ["DreamForge video", "Chronomaster DFA (dfa)"];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg[format:dfa]"];
}
