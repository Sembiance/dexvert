import {xu} from "xu";
import {Format} from "../../Format.js";

export class stardockEntertainmentVideo extends Format
{
	name           = "Stardock Entertainment Video";
	website        = "https://wiki.multimedia.cx/index.php/Stardock_VDO";
	ext            = [".sdv", ".vdo"];
	forbidExtMatch = true;
	magic          = ["Stardock Entertainment Video"];
	converters     = ["na_game_tool[format:sdv]"];
}

