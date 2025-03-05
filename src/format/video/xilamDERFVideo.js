import {Format} from "../../Format.js";

export class xilamDERFVideo extends Format
{
	name           = "Xilam DERF Video";
	website        = "https://wiki.multimedia.cx/index.php/Xilam_DERF";
	ext            = [".vds", ".vdo"];
	forbidExtMatch = true;
	magic          = ["Xilam DERF video"];
	weakMagic      = true;
	converters     = ["na_game_tool[format:derf-vid]"];
}
