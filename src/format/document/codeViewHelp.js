import {Format} from "../../Format.js";

export class codeViewHelp extends Format
{
	name           = "Codeview Help";
	ext            = [".hlp"];
	forbidExtMatch = true;
	magic          = ["Codeview Help"];
	converters     = ["strings"];
}
