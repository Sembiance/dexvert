import {Format} from "../../Format.js";

export class wordWorth extends Format
{
	name       = "WordWorth";
	magic      = ["IFF data, WOWO Wordworth document", "WordWorth document"];
	converters = ["WoW[outType:rtf]", "WoW[outType:asc]", "iff_convert", "strings"];
}
