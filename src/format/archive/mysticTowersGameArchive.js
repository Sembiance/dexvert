import {Format} from "../../Format.js";

export class mysticTowersGameArchive extends Format
{
	name           = "Mystic Towers Game Archive";
	website        = "https://moddingwiki.shikadi.net/wiki/DAT_Format_(Mystic_Towers)";
	ext            = [".dat"];
	forbidExtMatch = true;
	filename       = [/mystus\.dat$/i];
	converters     = ["gamearch"];
}
