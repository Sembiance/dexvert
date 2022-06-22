import {Format} from "../../Format.js";

export class textEngine extends Format
{
	name           = "Text Engine Document";
	ext            = [".std"];
	forbidExtMatch = true;
	magic          = ["TextEngine document (generic)", "TextEngine document (v4.0)", "TextEngine document (v5.2)"];
	weakMagic      = ["TextEngine document (generic)"];
	converters     = ["strings"];
}
