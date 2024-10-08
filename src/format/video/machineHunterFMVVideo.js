import {xu} from "xu";
import {Format} from "../../Format.js";

export class machineHunterFMVVideo extends Format
{
	name           = "Machine Hunter FMV Video";
	website        = "https://wiki.multimedia.cx/index.php/Machine_Hunter_FMV";
	ext            = [".fmv"];
	forbidExtMatch = true;
	magic          = ["Machine Hunter FMV Video"];
	weakMagic      = true;
	converters     = ["na_game_tool[format:mh-fmv]"];
}
