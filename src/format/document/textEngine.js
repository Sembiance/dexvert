import {Format} from "../../Format.js";

export class textEngine extends Format
{
	name           = "Text Engine Document";
	ext            = [".std"];
	forbidExtMatch = true;
	magic          = ["TextEngine document"];
	trustMagic     = true;
	converters     = ["strings"];
}
