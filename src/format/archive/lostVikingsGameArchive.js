import {Format} from "../../Format.js";

export class lostVikingsGameArchive extends Format
{
	name           = "The Lost Vikings Game Archive";
	website        = "https://moddingwiki.shikadi.net/wiki/The_Lost_Vikings";
	ext            = [".dat"];
	forbidExtMatch = true;
	filename       = [/^data\.dat$/i];
	magic          = [/^geArchive: DAT_26( |$)/];
	converters     = ["gameextractor[codes:DAT_26]", "gamearch"];
}
