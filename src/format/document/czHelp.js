import {Format} from "../../Format.js";

export class czHelp extends Format
{
	name           = "CZ Help";
	ext            = ["hlp"];
	forbidExtMatch = true;
	magic          = ["CZ Help"];
	converters     = ["strings"];
}
