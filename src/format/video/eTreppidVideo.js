import {xu} from "xu";
import {Format} from "../../Format.js";

export class eTreppidVideo extends Format
{
	name           = "eTreppid Video";
	website        = "https://wiki.multimedia.cx/index.php/ETV";
	ext            = [".etv"];
	forbidExtMatch = true;
	magic          = ["eTreppid video"];
	converters     = ["na_game_tool[format:etv]"];
}
