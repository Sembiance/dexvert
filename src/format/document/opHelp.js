import {Format} from "../../Format.js";

export class opHelp extends Format
{
	name           = "OPHelp";
	ext            = [".hlp"];
	forbidExtMatch = true;
	magic          = ["OPHelp Help", "Object Professional Help"];
	converters     = ["vibe2rtf"];
}
