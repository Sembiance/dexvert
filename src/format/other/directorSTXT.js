import {Format} from "../../Format.js";

export class directorSTXT extends Format
{
	name           = "Director STXT";
	ext            = [".stxt"];
	forbidExtMatch = true;
	magic          = ["Director STXT"];
	weakMagic      = true;
	converters     = ["strings"];
}
