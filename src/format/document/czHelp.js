import {Format} from "../../Format.js";

export class czHelp extends Format
{
	name           = "CZ Help";
	website        = "http://fileformats.archiveteam.org/wiki/CZ_Help";
	ext            = [".hlp"];
	forbidExtMatch = true;
	magic          = ["CZ Help"];
	converters     = ["strings"];
}
