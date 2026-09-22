import {Format} from "../../Format.js";

export class digitalPicturesFCAT extends Format
{
	name           = "Digital Pictures FCAT";
	ext            = [".gam"];
	forbidExtMatch = true;
	magic          = ["Digital Pictures FCAT"];
	converters     = ["na_game_tool_extract[format:fcat]"];
}

