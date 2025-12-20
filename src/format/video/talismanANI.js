import {xu} from "xu";
import {Format} from "../../Format.js";

export class talismanANI extends Format
{
	name           = "Talisman ANI";
	website        = "https://wiki.multimedia.cx/index.php/Talisman_ANI";
	ext            = [".ani"];
	forbidExtMatch = true;
	magic          = ["Talisman ANI", "Talisman game Animation"];
	converters     = ["na_game_tool[format:talisman]"];
}
