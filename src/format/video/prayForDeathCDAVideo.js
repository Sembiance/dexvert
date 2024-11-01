import {xu} from "xu";
import {Format} from "../../Format.js";

export class prayForDeathCDAVideo extends Format
{
	name           = "Pray for Death CDA Video";
	website        = "https://wiki.multimedia.cx/index.php/Pray_for_Death_CDA";
	ext            = [".cda"];
	forbidExtMatch = true;
	magic          = ["Pray for Death CDA Video", "Pray for Death cutscene"];
	converters     = ["na_game_tool[format:cda]"];
}
