import {Format} from "../../Format.js";

export class amigaMurder extends Format
{
	name       = "Amiga Murder Film";
	website    = "https://wiki.multimedia.cx/index.php/Murder_FILM";
	ext        = [".film"];
	magic      = ["Amiga Murder video"];
	converters = ["na_game_tool[format:mfilm]"];
}
