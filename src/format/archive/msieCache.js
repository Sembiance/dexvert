import {Format} from "../../Format.js";

export class msieCache extends Format
{
	name           = "Microsoft Internet Explorer Cache";
	ext            = [".dat"];
	forbidExtMatch = true;
	filename       = [/^index\.dat$/i];
	magic          = ["Microsoft Internet Explorer cache", "Internet Explorer cache file", "Internet Explorer Cache Datei"];
	converters     = ["vibeExtract"];
}
