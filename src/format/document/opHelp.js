import {Format} from "../../Format.js";

export class opHelp extends Format
{
	name           = "OPHelp";
	ext            = [".hlp"];
	forbidExtMatch = true;
	magic          = ["OPHelp Help"];
	converters     = ["vibe2rtf"];
}
