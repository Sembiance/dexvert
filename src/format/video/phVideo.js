import {xu} from "xu";
import {Format} from "../../Format.js";

export class phVideo extends Format
{
	name           = "PH Video";
	website        = "https://wiki.multimedia.cx/index.php/PH_Video";
	ext            = [".ph"];
	forbidExtMatch = true;
	magic          = ["PH video"];
	weakMagic      = true;
	converters     = ["na_game_tool[format:ph]"];
}
