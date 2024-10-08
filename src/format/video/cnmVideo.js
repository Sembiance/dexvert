import {xu} from "xu";
import {Format} from "../../Format.js";

export class cnmVideo extends Format
{
	name           = "CNM Video";
	website        = "https://wiki.multimedia.cx/index.php/CNM";
	ext            = [".cnm", ".ci2"];
	forbidExtMatch = true;
	magic          = ["CNM video"];
	converters     = ["na_game_tool[format:cnm]", "na_game_tool[format:ci2]"];
}
