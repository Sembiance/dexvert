import {Format} from "../../Format.js";

export class follinPlayer extends Format
{
	name         = "Follin Player Module";
	website      = "http://fileformats.archiveteam.org/wiki/Follin_Player_II";
	ext          = [".tf"];
	magic        = ["Follin Player II module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
