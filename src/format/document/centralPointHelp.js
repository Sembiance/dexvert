import {Format} from "../../Format.js";

export class centralPointHelp extends Format
{
	name           = "Central Point Help";
	ext            = [".hlp"];
	forbidExtMatch = true;
	magic          = ["Central Point Software Help data"];
	converters     = ["strings"];
}
