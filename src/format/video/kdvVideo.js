import {Format} from "../../Format.js";

export class kdvVideo extends Format
{
	name           = "KDV video";
	website        = "https://wiki.multimedia.cx/index.php/KDV";
	ext            = [".kdv"];
	forbidExtMatch = true;
	magic          = ["KDV Video"];
	converters     = ["na_game_tool"];
}
