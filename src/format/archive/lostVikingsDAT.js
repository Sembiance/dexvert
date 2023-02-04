import {Format} from "../../Format.js";

export class lostVikingsDAT extends Format
{
	name           = "The Lost Vikings DAT Archive";
	website        = "https://moddingwiki.shikadi.net/wiki/The_Lost_Vikings";
	ext            = [".dat"];
	forbidExtMatch = true;
	filename       = [/^data\.dat$/i];
	converters     = ["gamearch"];
}
