import {Format} from "../../Format.js";

export class gunmetalSBVVideo extends Format
{
	name           = "Gunmetal SBV Video";
	ext            = [".sbv"];
	forbidExtMatch = true;
	magic          = ["Gunmetal SBV Video"];
	converters     = ["na_game_tool[format:sbv]"];
}

