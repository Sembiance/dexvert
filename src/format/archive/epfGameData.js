import {Format} from "../../Format.js";

export class epfGameData extends Format
{
	name       = "EPF Game Data Archive";
	website    = "https://moddingwiki.shikadi.net/wiki/EPF_Format";
	ext        = [".epf"];
	magic      = ["EPF game data archive"];
	converters = ["gamearch", "gameextractor"];
}
