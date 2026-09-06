import {Format} from "../../Format.js";

export class whalesVoyageIILSD extends Format
{
	name           = "Whale's Voyage II LSD Video";
	ext            = [".lsd"];
	forbidExtMatch = true;
	magic          = ["Whale's Voyage II LSD"];
	converters     = ["na_game_tool[format:lsd]"];
}
