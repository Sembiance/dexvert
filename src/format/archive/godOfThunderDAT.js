import {Format} from "../../Format.js";

export class godOfThunderDAT extends Format
{
	name       = "God of Thunder DAT Archive";
	website    = "https://moddingwiki.shikadi.net/wiki/DAT_Format_(God_of_Thunder)";
	filename   = [/^gotres\.dat$/i];
	converters = ["gamearch"];
}
