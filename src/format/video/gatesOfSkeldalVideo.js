import {Format} from "../../Format.js";

export class gatesOfSkeldalVideo extends Format
{
	name           = "Gates of Skeldal Video";
	ext            = [".mgf"];
	forbidExtMatch = true;
	magic          = ["Gates of Skeldal Video"];
	converters     = ["na_game_tool[format:mgif]"];
}
