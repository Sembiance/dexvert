import {Format} from "../../Format.js";

export class obfuscatedAVI extends Format
{
	name           = "Obfuscated AVI";
	ext            = [".avi"];
	forbidExtMatch = true;
	magic          = ["Obfuscated AVI"];
	packed         = true;
	converters     = ["na_game_tool_extract[format:avi_obf]"];
}
