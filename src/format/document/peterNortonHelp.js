import {Format} from "../../Format.js";

export class peterNortonHelp extends Format
{
	name           = "Peter Norton Computing Help";
	ext            = [".hlp"];
	forbidExtMatch = true;
	magic          = ["Peter Norton Computing Help"];
	converters     = ["strings"];
}
