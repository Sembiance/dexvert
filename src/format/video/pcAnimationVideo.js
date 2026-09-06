import {Format} from "../../Format.js";

export class pcAnimationVideo extends Format
{
	name           = "PC-Animation video";
	ext            = [".ani"];
	forbidExtMatch = true;
	magic          = ["PC-Animation video"];
	converters     = ["na_game_tool[format:pcanim]"];
}

