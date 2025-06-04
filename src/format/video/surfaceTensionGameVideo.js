import {Format} from "../../Format.js";

export class surfaceTensionGameVideo extends Format
{
	name           = "Surface Tension/Soul Hunt Video";
	website        = "https://wiki.multimedia.cx/index.php/Soul_Hunt_VID";
	ext            = [".vid"];
	forbidExtMatch = true;
	magic          = ["Surface Tension game video"];
	converters     = ["na_game_tool[format:soulhunt]"];
}
