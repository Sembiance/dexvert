import {Format} from "../../Format.js";

export class godOfThunderGameArchive extends Format
{
	name           = "God of Thunder Game Archive";
	website        = "https://moddingwiki.shikadi.net/wiki/DAT_Format_(God_of_Thunder)";
	ext            = [".dat"];
	forbidExtMatch = true;
	filename       = [/^gotres\.dat$/i];
	converters     = ["gamearch"];
}
