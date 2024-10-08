import {xu} from "xu";
import {Format} from "../../Format.js";

export class interspectiveAnimation extends Format
{
	name           = "Interspective Animation";
	website        = "https://wiki.multimedia.cx/index.php/Interspective_animation";
	ext            = [".dat"];
	forbidExtMatch = true;
	filename       = [/^iuc_f\d\d.dat$/i, /^gbg_f\d\d.dat$/i];
	converters     = ["na_game_tool[format:guilty]"];
}
