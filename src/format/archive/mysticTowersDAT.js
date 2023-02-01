import {Format} from "../../Format.js";

export class mysticTowersDAT extends Format
{
	name       = "Mystic Towers DAT Archive";
	website    = "https://moddingwiki.shikadi.net/wiki/DAT_Format_(Mystic_Towers)";
	ext        = [".dat"];
	weakExt    = [".dat"];
	filename   = [/^rgmystus\.dat$/i];
	converters = ["gamearch"];
}
