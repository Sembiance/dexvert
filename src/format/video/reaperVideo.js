import {Format} from "../../Format.js";

export class reaperVideo extends Format
{
	name           = "Reaper video";
	website        = "https://wiki.multimedia.cx/index.php/Reaper";
	ext            = [".fmv"];
	forbidExtMatch = true;
	magic          = ["Reaper video"];
	converters     = ["na_game_tool[format:reaper-fmv]"];
}
