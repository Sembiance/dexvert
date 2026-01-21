import {Format} from "../../Format.js";

export class spectrumHolobyteFVF extends Format
{
	name           = "Spectrum Holobyte FVF Video";
	ext            = [".fvf"];
	forbidExtMatch = true;
	magic          = ["STNG 'A Final Unity' Fullmotion Video cutscene File"];
	converters     = ["na_game_tool[format:fvf]"];
}
