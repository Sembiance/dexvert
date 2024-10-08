import {xu} from "xu";
import {Format} from "../../Format.js";

export class crhVideo extends Format
{
	name           = "CRH Video";
	website        = "https://wiki.multimedia.cx/index.php/CRH";
	ext            = [".crh"];
	forbidExtMatch = true;
	magic          = ["CRH Video"];
	converters     = ["na_game_tool[format:crh-de]", "na_game_tool[format:crh-nc]"];
}
