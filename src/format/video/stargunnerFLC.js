import {Format} from "../../Format.js";

export class stargunnerFLC extends Format
{
	name           = "Stargunner FLC Video";
	ext            = [".flc"];
	forbidExtMatch = true;
	magic          = ["Stargunner FLC"];
	converters     = ["na_game_tool[format:sg_flc]"];
}
