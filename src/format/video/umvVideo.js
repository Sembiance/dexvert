import {xu} from "xu";
import {Format} from "../../Format.js";

export class umvVideo extends Format
{
	name           = "UMV Video";
	website        = "https://wiki.multimedia.cx/index.php/UMV";
	ext            = [".umv"];
	forbidExtMatch = true;
	magic          = [/^UMV Video$/];
	converters     = ["na_game_tool[format:umv-dracula]", "na_game_tool[format:umv-afraid]"];
}
